"""Builder agent that consumes terrain maps and constructs structures."""
from typing import Dict, Any
import time

from .base_agent import BaseAgent
from ..messaging.message import Message
from ..messaging.enums.message_status import MessageStatus
from ..messaging.enums.message_types import MessageType
from ..domain.inventory import Inventory
from ..domain.map_data import MapData
from ..domain.bom import BOM, BOMPhase
from ..construction.build_executor import BuildExecutor
from ..construction.templates.template_registry import get_template, list_templates


class BuilderAgent(BaseAgent):
    """
    Builder agent workflow:
    1. Receives SEND_TERRAIN_DATA_MAP → stores map_data
    2. Receives BUILDER_SEND_BOM → generates BOM and requests materials
    3. Receives UPDATES_ON_INVENTORY → tracks materials, transitions to RUNNING if ready
    4. START_MAIN_ACTION → begins construction if materials available
       - As materials arrive → constructs phases sequentially
    """

    def __init__(self, mc_client):
        super().__init__("builder", mc_client)

        # Domain models
        self.map_data: MapData | None = None
        self.bom: BOM | None = None
        self.inventory = Inventory()

        # Template system
        self.current_template = get_template("table")  # default template

        # State tracking
        self.current_phase: BOMPhase | None = None
        self.last_material_time = 0.0
        self.TIMEOUT_LIMIT = 120  # seconds

        # Coordinator reference (injected by loader)
        self._coordinator_ref = None

    # ======== Message Processing ========

    def process_message(self, message: Message) -> None:
        """
        Routes incoming messages to handlers.
        State transitions and data updates happen here.
        """
        msg_type = message.message_type
        payload = message.payload if isinstance(message.payload, dict) else {}

        if msg_type == MessageType.START_MAIN_ACTION.value:
            self._handle_start_build()

        elif msg_type == MessageType.PAUSE_AGENT.value:
            self.state_manager.transition(MessageStatus.PAUSED, "Pausat")
            self.mc.postToChat("[Builder] Pausat")

        elif msg_type == MessageType.RESUME_AGENT.value:
            self.state_manager.transition(MessageStatus.RUNNING, "Repres")
            self.mc.postToChat("[Builder] Repres")

        elif msg_type == MessageType.STOP_AGENT.value:
            self.state_manager.transition(MessageStatus.STOPPED, "Aturat")
            self._reset_state()
            self.mc.postToChat("[Builder] Aturat")

        elif msg_type == MessageType.SEND_TERRAIN_DATA_MAP.value:
            self._handle_terrain_map(payload)

        elif msg_type == MessageType.BUILDER_SEND_BOM.value:
            self._handle_bom_request(payload)

        elif msg_type == MessageType.UPDATES_ON_INVENTORY.value:
            self._handle_inventory_update(payload)

        elif msg_type == MessageType.SHOW_STATUS.value:
            self._report_status()

        elif msg_type == MessageType.BUILDER_NEW_PLAN.value:
            template_name = payload.get("template") if isinstance(payload, dict) else None
            self._switch_template(template_name)

        elif msg_type == MessageType.SHOW_BUILDER_PLANS.value:
            self._show_templates()

        else:
            self.log.warning(f"Missatge no reconegut: {msg_type}")

    # ======== Perception-Decision-Action Cycle ========

    def perceive(self) -> Dict[str, Any]:
        """Assess current state: do we have map, BOM, materials, and BOM completion?"""
        current_material = None
        current_need = 0
        current_have = 0

        if self.current_phase:
            current_material = self.current_phase.material
            current_need = self.current_phase.amount
            current_have = self.inventory.available(current_material)

        # Check if entire BOM is satisfied
        bom_all_satisfied = False
        if self.bom:
            all_satisfied = True
            for phase in self.bom.phases:
                have = self.inventory.available(phase.material)
                if have < phase.amount:
                    all_satisfied = False
                    break
            bom_all_satisfied = all_satisfied

        return {
            "map_ready": self.map_data is not None,
            "bom_ready": self.bom is not None,
            "bom_all_satisfied": bom_all_satisfied,
            "current_phase": self.current_phase,
            "current_material": current_material,
            "current_need": current_need,
            "current_have": current_have,
            "inventory": self.inventory.stock.copy(),
        }

    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Decide next action based on perception and state."""
        
        # If not running, no action
        if not self.state_manager.is_running():
            return {"action": "idle"}

        # Timeout check while waiting
        if self._is_timeout():
            return {"action": "timeout"}

        # If we have a current phase and enough materials, build it
        phase = perception.get("current_phase")
        if phase:
            have = perception.get("current_have", 0)
            need = perception.get("current_need", 0)

            if have >= need:
                return {"action": "build_phase", "phase": phase}
            else:
                # Not enough materials yet; stay waiting
                return {"action": "wait_materials"}

        return {"action": "idle"}

    def act(self, action: Dict[str, Any]) -> None:
        """Execute the decided action."""
        action_type = action.get("action")

        if action_type == "build_phase":
            phase = action.get("phase")
            if phase:
                self._execute_phase(phase)
                self._advance_phase()

        elif action_type == "timeout":
            self.state_manager.transition(MessageStatus.ERROR, "Materials timeout")
            self.mc.postToChat("[Builder] Error: materials no rebuts a temps")

        elif action_type in {"wait_materials", "idle"}:
            pass

    # ======== Internal Handlers ========

    def _handle_start_build(self) -> None:
        """Handle START command: begin construction if ready."""
        if not self.map_data:
            self.mc.postToChat("[Builder] Error: cap dades de mapa. Espera l'Explorer.")
            return

        if not self.bom:
            self.mc.postToChat("[Builder] Error: cap BOM. Genereu primer amb 'builder bom'.")
            return

        # Idempotency: if already running (either building or waiting for materials), do nothing
        if self.state_manager.is_running():
            self.mc.postToChat("[Builder] Ja estas construint")
            return

        # Reset to first phase
        self.current_phase = self.bom.current_phase()
        if not self.current_phase:
            self.mc.postToChat("[Builder] Error: BOM buit, res a construir.")
            return

        # Check if we have materials for first phase
        have = self.inventory.available(self.current_phase.material)
        need = self.current_phase.amount

        if have >= need:
            self.state_manager.transition(MessageStatus.RUNNING, "Iniciant construccio")
            self.mc.postToChat(
                f"[Builder] Iniciant construccio (tenim {have}/{need} {self.current_phase.material})"
            )
        else:
            # Wait for materials
            self.state_manager.transition(MessageStatus.RUNNING, "Esperant materials")
            self.mc.postToChat(
                f"[Builder] Esperant materials ({have}/{need} {self.current_phase.material})"
            )
            self.last_material_time = time.time()

    def _handle_terrain_map(self, payload: Dict[str, Any]) -> None:
        """Store terrain map from Explorer."""
        try:
            origin = tuple(payload.get("origin", (0, 0, 0)))
            flat_region = payload.get("flat_region", [])
            obstacles = payload.get("obstacles", [])
            elevation_map = payload.get("elevation_map", {})

            self.map_data = MapData(
                origin=origin,
                elevation_map=elevation_map,
                flat_region=flat_region,
                obstacles=obstacles,
            )
            self.log.info(f"Mapa rebut: {self.map_data}")
            self.mc.postToChat("[Builder] Mapa rebut de l'Explorer")
        except Exception as e:
            self.log.error(f"Error processant mapa: {e}")
            self.state_manager.transition(MessageStatus.ERROR, f"Mapa invàlid: {e}")

    def _handle_bom_request(self, payload: Dict[str, Any]) -> None:
        """Generate BOM and request all materials from Miner in one message."""
        if not self.map_data:
            self.mc.postToChat("[Builder] Error: cap dades de mapa. Espera l'Explorer.")
            return

        if not self.current_template:
            self.mc.postToChat("[Builder] Error: cap template seleccionat.")
            return

        # Generate BOM using current template
        self.bom = self.current_template.generate_bom(self.map_data)
        self.current_phase = self.bom.current_phase()

        self.mc.postToChat(f"[Builder] BOM generat amb '{self.current_template.name}' ({len(self.bom.phases)} fases)")

        # Send ALL material requests to Miner in ONE message
        if not self._coordinator_ref:
            self.log.warning("No coordinator per enviar BOM")
            return

        # Aggregate all materials across all phases
        total_materials = {}
        for phase in self.bom.phases:
            material = phase.material
            amount = phase.amount
            total_materials[material] = total_materials.get(material, 0) + amount

        # Send ONE BOM message with all materials
        try:
            bom_payload = {
                "materials": [
                    {"material": mat, "amount": amt}
                    for mat, amt in total_materials.items()
                ]
            }
            self._coordinator_ref.send_control(
                "miner",
                MessageType.BUILDER_SEND_BOM.value,
                bom_payload,
            )
            materials_str = ", ".join(f"{amt} {mat}" for mat, amt in total_materials.items())
            self.mc.postToChat(f"[Builder] BOM enviat al Miner: {materials_str}")
        except Exception as e:
            self.log.error(f"Error enviant BOM: {e}")
        
        self.last_material_time = time.time()

    def _handle_inventory_update(self, payload: Dict[str, Any]) -> None:
        """Handle material delivery or progress update from Miner."""
        # Case 1: All materials delivered from fulfilled BOM
        materials_list = payload.get("materials")
        if materials_list and isinstance(materials_list, list):
            self.mc.postToChat("[Builder] Rebent materials del Miner...")
            total_items = 0
            for item in materials_list:
                if isinstance(item, dict):
                    material = item.get("material")
                    amount = item.get("amount")
                    if material and isinstance(amount, int):
                        self.inventory.add(material, amount)
                        total_items += amount
                        self.mc.postToChat(f"  + {amount} {material}")
            
            self.last_material_time = time.time()
            self.mc.postToChat(f"[Builder] Total rebut: {total_items} blocs")
            
            # Check if BOM is now completely satisfied
            if self.bom and self._is_bom_complete():
                self.mc.postToChat("[Builder] Tots els materials rebuts! Iniciant construccio automaticament...")
                self._auto_start_build()
            
            return

        # Case 2: Progress update during fulfillment
        progress_list = payload.get("progress")
        if progress_list and isinstance(progress_list, list):
            summary = []
            for item in progress_list:
                if isinstance(item, dict):
                    mat = item.get("material")
                    pct = item.get("completion_pct", 0)
                    summary.append(f"{mat}:{pct}%")
            if summary:
                self.mc.postToChat(f"[Builder] Progres: {', '.join(summary)}")
            return



    def _report_status(self) -> None:
        """Report current builder status."""
        state = self.state_manager.state
        phase_str = self.current_phase.name if self.current_phase else "none"
        inv_str = ", ".join(f"{k}:{v}" for k, v in self.inventory.stock.items()) or "empty"
        template_str = self.current_template.name if self.current_template else "none"
        self.mc.postToChat(f"[Builder] Estat: {state}, Fase: {phase_str}")
        self.mc.postToChat(f"[Builder] Template: {template_str}, Inventari: {inv_str}")

    def _switch_template(self, template_name: str | None) -> None:
        """Switch to a different construction template."""
        if not template_name:
            self.mc.postToChat("[Builder] Error: cap nom de template proporcionat")
            return

        template = get_template(template_name)
        if template:
            self.current_template = template
            self.mc.postToChat(f"[Builder] Template establert a '{template_name}'")
            self.log.info(f"Template canviat a: {template_name}")
        else:
            available = ", ".join(list_templates())
            self.mc.postToChat(f"[Builder] Error: template desconegut '{template_name}'")
            self.mc.postToChat(f"[Builder] Disponibles: {available}")

    def _show_templates(self) -> None:
        """List all available templates."""
        available = ", ".join(list_templates())
        self.mc.postToChat(f"[Builder] Templates disponibles: {available}")

    def _execute_phase(self, phase: BOMPhase) -> None:
        """Execute a single construction phase using template geometry."""
        try:
            if not self.map_data or not self.current_template:
                self.log.error("No map data or template for execution")
                return

            # Get template build positions
            origin = self._select_build_origin()
            positions = self.current_template.get_build_positions(origin)

            if not positions or phase.name not in positions:
                self.log.warning(f"No positions defined for phase {phase.name}")
                return

            # Create plan from template positions
            phase_blocks = positions[phase.name]
            phase_plan = [{
                "phase": phase.name,
                "material": phase.material,
                "blocks": [(x, y, z) for x, y, z, mat in phase_blocks if mat == phase.material]
            }]

            # Execute blocks
            executor = BuildExecutor(self.mc, self.inventory)
            executor.execute(phase_plan)

            self.mc.postToChat(f"[Builder] Fase '{phase.name}' construïda")
            self.log.info(f"Fase completada: {phase.name}")

        except Exception as e:
            self.log.error(f"Error executant fase: {e}")
            self.state_manager.transition(MessageStatus.ERROR, str(e))
            self.mc.postToChat(f"[Builder] Error: {e}")

    def _select_build_origin(self) -> tuple[int, int, int]:
        """Select build origin from map flat region."""
        if not self.map_data:
            return (0, 64, 0)
        
        origin = self.map_data.origin
        if origin in self.map_data.flat_region:
            return origin
        
        if self.map_data.flat_region:
            return tuple(self.map_data.flat_region[0])
        
        return origin

    def _advance_phase(self) -> None:
        """Move to next phase or finish."""
        if self.bom:
            self.bom.advance()
            self.current_phase = self.bom.current_phase()

            if not self.current_phase:
                # All phases complete
                self.state_manager.transition(MessageStatus.IDLE, "Construccio completada")
                self.mc.postToChat("[Builder] Construccio completada!")

                # Notify other agents
                if self._coordinator_ref:
                    try:
                        self._coordinator_ref.send_control(
                            "ALL",
                            MessageType.CONFIRM_COMPLETION_OF_BUILD.value,
                            {},
                        )
                    except Exception as e:
                        self.log.error(f"Error enviant confirmacio: {e}")
            else:
                # Check if we have materials for next phase
                have = self.inventory.available(self.current_phase.material)
                need = self.current_phase.amount

                if have >= need:
                    self.mc.postToChat(f"[Builder] Fase '{self.current_phase.name}' a punt")
                else:
                    self.mc.postToChat(
                        f"[Builder] Esperant materials per '{self.current_phase.name}' ({have}/{need})"
                    )

    def _is_bom_complete(self) -> bool:
        """Check if all BOM materials are in inventory."""
        if not self.bom:
            return False
        
        for phase in self.bom.phases:
            have = self.inventory.available(phase.material)
            if have < phase.amount:
                return False
        
        return True

    def _auto_start_build(self) -> None:
        """Automatically start building when BOM materials are complete."""
        if not self.bom:
            self.log.warning("No BOM to build")
            return
        
        # Reset to first phase
        self.current_phase = self.bom.current_phase()
        if not self.current_phase:
            self.mc.postToChat("[Builder] Error: BOM buit, res a construir.")
            return
        
        # Transition to RUNNING and begin construction cycle
        self.state_manager.transition(MessageStatus.RUNNING, "Construccio en progress")
        self.mc.postToChat(f"[Builder] Iniciant construccio amb {len(self.bom.phases)} fases")
        self.last_material_time = time.time()

    def _is_timeout(self) -> bool:
        """Check if material delivery has timed out."""
        if not self.last_material_time:
            return False
        return (time.time() - self.last_material_time) > self.TIMEOUT_LIMIT

    def _reset_state(self) -> None:
        """Reset internal state on stop."""
        self.map_data = None
        self.bom = None
        self.current_phase = None
        self.last_material_time = 0.0
        self.inventory = Inventory()

    # ======== Hooks ========

    def set_coordinator(self, coordinator):
        """Inject coordinator reference for sending messages to other agents."""
        self._coordinator_ref = coordinator

    def on_start(self) -> None:
        pass

    def on_stop(self) -> None:
        self._reset_state()
