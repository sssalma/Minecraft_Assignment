"""Miner agent that mines materials and fulfills BOM requests."""
from typing import Dict, Any
import time

from .base_agent import BaseAgent
from ..messaging.message import Message
from ..messaging.enums.message_status import MessageStatus
from ..messaging.enums.message_types import MessageType
from ..domain.inventory import Inventory
from ..mining_strategies.strategy_registry import get_strategy, list_strategies


class MinerAgent(BaseAgent):
    """
    Miner agent workflow:
    1. Receives BUILDER_SEND_BOM → stores material request (doesn't start mining)
    2. User sends START_MAIN_ACTION → mines freely (ignores BOM if present)
    3. User sends FULFILL_INVENTORY → mines only to fulfill pending BOM
    4. During fulfillment → periodically reports progress
    5. When BOM fulfilled → sends materials to builder
    6. MINER_NEW_STRATEGY → switches mining strategy
    """

    def __init__(self, mc_client):
        super().__init__("miner", mc_client)

        # Domain models
        self.inventory = Inventory()

        # Initial stock with variety of materials
        self.inventory.add("stone", 3)
        self.inventory.add("wood", 3)
        self.inventory.add("dirt", 3)
        self.inventory.add("sand", 3)
        self.inventory.add("gravel", 3)

        # Track what was mined in current operation
        self.mined_materials: Dict[str, int] = {}  # {"stone": 15, "wood": 8, ...}

        # Mining strategy (default: vertical)
        self.current_strategy = get_strategy("vertical")

        # BOM request tracking
        self.bom_request: Dict[str, int] | None = None  # {"material": amount, ...} all materials needed
        self.bom_request_original: Dict[str, int] | None = None  # Original request for completion check
        self.mining_coords: tuple[int, int, int] | None = None
        self.last_inventory_report = 0.0
        self.REPORT_INTERVAL = 3  # seconds between progress reports

        # Coordinator reference
        self._coordinator_ref = None

    # ======== Message Processing ========

    def process_message(self, message: Message) -> None:
        """Routes incoming messages to handlers."""
        msg_type = message.message_type
        payload = message.payload if isinstance(message.payload, dict) else {}

        if msg_type == MessageType.START_MAIN_ACTION.value:
            self._handle_start_mining(payload)

        elif msg_type == MessageType.PAUSE_AGENT.value:
            self.state_manager.transition(MessageStatus.PAUSED, "Pausat")
            self.mc.postToChat("[Miner] Pausat")

        elif msg_type == MessageType.RESUME_AGENT.value:
            self.state_manager.transition(MessageStatus.RUNNING, "Repres")
            self.mc.postToChat("[Miner] Repres")

        elif msg_type == MessageType.STOP_AGENT.value:
            self.state_manager.transition(MessageStatus.STOPPED, "Aturat")
            self._reset_state()
            self.mc.postToChat("[Miner] Aturat")

        elif msg_type == MessageType.BUILDER_SEND_BOM.value:
            self._handle_bom_request(payload)

        elif msg_type == MessageType.FULFILL_INVENTORY.value:
            self._handle_fulfill_request()

        elif msg_type == MessageType.MINER_NEW_STRATEGY.value:
            strategy_name = payload.get("strategy") if isinstance(payload, dict) else None
            self._switch_strategy(strategy_name)

        elif msg_type == MessageType.SHOW_MINER_STRATEGIES.value:
            self._show_strategies()

        elif msg_type == MessageType.SHOW_STATUS.value:
            self._report_status()

        else:
            self.log.warning(f"Missatge no reconegut: {msg_type}")

    # ======== Perception-Decision-Action Cycle ========

    def perceive(self) -> Dict[str, Any]:
        """Assess current inventory and BOM request state."""
        bom_completion = {}
        total_need = 0
        total_have = 0

        if self.bom_request:
            for material, need in self.bom_request.items():
                have = self.inventory.available(material)
                bom_completion[material] = {"need": need, "have": have}
                total_need += need
                total_have += have

        return {
            "bom_request": self.bom_request,
            "bom_completion": bom_completion,
            "total_need": total_need,
            "total_have": total_have,
            "inventory": self.inventory.stock.copy(),
        }

    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Decide what to do based on current state (mainly for periodic status reports)."""
        # Allow progress reporting even if not running when a BOM is pending
        if not self.state_manager.is_running():
            bom_pending = perception.get("bom_request")
            if not bom_pending:
                return {"action": "idle"}

        # If fulfilling a BOM and periodic report time reached, report progress
        bom = perception.get("bom_request")
        if not bom:
            return {"action": "idle"}

        # Check if we should send periodic progress report
        current_time = time.time()
        if current_time - self.last_inventory_report > self.REPORT_INTERVAL:
            completion = perception.get("bom_completion", {})
            incomplete = [m for m, d in completion.items() if d["have"] < d["need"]]
            if incomplete:
                return {"action": "report_progress"}

        return {"action": "idle"}

    def act(self, action: Dict[str, Any]) -> None:
        """Execute decided action (mainly periodic reports)."""
        action_type = action.get("action")

        if action_type == "report_progress":
            self._send_progress_update()

        elif action_type == "idle":
            pass

    # ======== Internal Handlers ========

    def _handle_start_mining(self, payload: Dict[str, Any]) -> None:
        """Handle START command: begin independent mining operation."""
        # Extract optional coordinates
        x = payload.get("x")
        y = payload.get("y")
        z = payload.get("z")

        if x is not None and y is not None and z is not None:
            self.mining_coords = (int(x), int(y), int(z))
            self.mc.postToChat(f"[Miner] Minant a ({x}, {y}, {z})")
        else:
            self.mining_coords = None
            self.mc.postToChat("[Miner] Minant a la posicio del jugador")

        # Start mining (independent of any BOM request)
        self.state_manager.transition(MessageStatus.RUNNING, "Minant materials")
        strategy_name = self.current_strategy.get_name() if self.current_strategy else "unknown"
        self.mc.postToChat(f"[Miner] Iniciant mineria ({strategy_name})")

        # Mine whatever blocks we can find
        # Amount depends on strategy: 125 for grid (5x5x5), 20 for vertical
        if strategy_name == "grid":
            amount_to_mine = 125  # Full 5x5x5 cube
        else:
            amount_to_mine = 30  # Default for other strategies
        
        try:
            if self.current_strategy:
                # Mine and get materials dict back (material param is just a hint)
                self.mined_materials = self.current_strategy.mine(self, "stone", amount_to_mine)
                total_mined = sum(self.mined_materials.values())
                
                if self.mined_materials:
                    mined_str = ", ".join(f"{k}:{v}" for k, v in self.mined_materials.items())
                    self.mc.postToChat(f"[Miner] Minat total: {total_mined} blocs ({mined_str})")
                else:
                    self.mc.postToChat(f"[Miner] No s'ha pogut minar materials")
                
                self.last_inventory_report = time.time()
                # If a BOM is pending, check if we've completed it
                if self.bom_request and self._coordinator_ref:
                    try:
                        # Check if BOM is now complete
                        if self._is_bom_complete():
                            # BOM complete! Send full delivery (not just progress)
                            self.mc.postToChat(f"[Miner] BOM completat! Enviant materials al Builder...")
                            self._send_materials_to_builder()
                            self.state_manager.transition(MessageStatus.IDLE, "BOM completat i enviat")
                        else:
                            # BOM not complete yet, just send progress
                            self._send_progress_update()
                            self.state_manager.transition(MessageStatus.IDLE, "Minat completat (BOM incomplet)")
                    except Exception as e:
                        self.log.error(f"Error enviant progres post-mineria: {e}")
                else:
                    # No BOM request, just finish
                    self.state_manager.transition(MessageStatus.IDLE, "Minat completat")
            else:
                self.log.error("No mining strategy set")
                self.state_manager.transition(MessageStatus.ERROR, "No strategy")
        except Exception as e:
            self.log.error(f"Error minant: {e}")
            self.state_manager.transition(MessageStatus.ERROR, str(e))

    def _handle_bom_request(self, payload: Dict[str, Any]) -> None:
        """
        Store consolidated BOM request from Builder with ALL materials needed.
        Payload format: {"materials": [{"material": "stone", "amount": 25}, ...]}
        """
        materials_list = payload.get("materials", [])
        
        if not materials_list or not isinstance(materials_list, list):
            self.log.error(f"Peticio BOM invalida: {payload}")
            return

        # Convert to dict format: {"stone": 25, "wood": 85, ...}
        self.bom_request = {}
        for item in materials_list:
            if isinstance(item, dict):
                mat = item.get("material")
                amt = item.get("amount")
                if mat and isinstance(amt, int) and amt > 0:
                    self.bom_request[mat] = self.bom_request.get(mat, 0) + amt
        
        if not self.bom_request:
            self.log.error("No valid materials in BOM request")
            return

        # Store original for completion check later
        self.bom_request_original = self.bom_request.copy()
        self.last_inventory_report = time.time()

        # Report what we received
        materials_summary = ", ".join(f"{amt} {mat}" for mat, amt in self.bom_request.items())
        self.mc.postToChat(f"[Miner] BOM rebut: {materials_summary}")
        self.mc.postToChat(f"[Miner] Usa 'miner fulfill' per complir aquesta peticio")
        
        # Send an initial progress snapshot so Builder sees current completion
        if self._coordinator_ref:
            try:
                self._send_progress_update()
            except Exception as e:
                self.log.error(f"Error enviant progres inicial: {e}")

    def _handle_fulfill_request(self) -> None:
        """
        Fulfill ALL pending BOM materials at once.
        Adds all required materials to inventory, then sends them all to builder.
        """
        if not self.bom_request:
            self.mc.postToChat("[Miner] Error: cap peticio BOM pendent")
            return

        # Check status of all materials
        self.mc.postToChat(f"[Miner] Completant BOM amb {len(self.bom_request)} tipus de materials...")

        all_fulfilled = True
        for material, required in self.bom_request.items():
            have = self.inventory.available(material)
            if have >= required:
                    self.mc.postToChat(f"  [OK] {material}: ja tenim prou ({have}/{required})")
            else:
                needed = required - have
                self.inventory.add(material, needed)
                self.mc.postToChat(f"  + {material}: afegint {needed} (tenim {have}, necessari {required})")
                all_fulfilled = False

        if all_fulfilled:
            self.mc.postToChat("[Miner] Tots els materials ja estaven disponibles!")

        # Now send ALL materials to builder
        self._send_materials_to_builder()

        # If there's a BOM pending, send progress snapshot after fulfillment
        if self.bom_request and self._coordinator_ref:
            try:
                self._send_progress_update()
            except Exception as e:
                self.log.error(f"Error enviant progres post-mineria: {e}")
    def _send_materials_to_builder(self) -> None:
        """Send ALL materials from BOM to builder and clear request."""
        if not self.bom_request or not self._coordinator_ref:
            return

        # Convert back to list format for builder
        materials_list = [
            {"material": mat, "amount": amt}
            for mat, amt in self.bom_request.items()
        ]

        # Verify we have everything before sending
        for material, amount in self.bom_request.items():
            have = self.inventory.available(material)
            if have < amount:
                self.log.warning(f"Inventari insuficient: {have}/{amount} {material}")
                return

        try:
            self._coordinator_ref.send_control(
                "builder",
                MessageType.UPDATES_ON_INVENTORY.value,
                {"materials": materials_list},
            )
            
            # Consume all from miner inventory
            for material, amount in self.bom_request.items():
                self.inventory.consume(material, amount)
                self.mined_materials[material] = amount
            
            materials_summary = ", ".join(f"{amt} {mat}" for mat, amt in self.bom_request.items())
            self.mc.postToChat(f"[Miner] Materials enviats al Builder: {materials_summary}")
            self.bom_request = None
            self.bom_request_original = None
            
            if self.state_manager.is_running():
                self.state_manager.transition(MessageStatus.IDLE, "BOM completat")
        except Exception as e:
            self.log.error(f"Error enviant materials: {e}")

    def _send_progress_update(self) -> None:
        """Send progress update to builder for all BOM materials."""
        if not self.bom_request or not self._coordinator_ref:
            return

        # Build progress summary
        progress_list = []
        for material, required in self.bom_request.items():
            have = self.inventory.available(material)
            completion_pct = int((have / required) * 100) if required > 0 else 0
            remaining = required - have
            progress_list.append({
                "material": material,
                "have": have,
                "need": required,
                "remaining": remaining,
                "completion_pct": completion_pct,
            })

        try:
            self._coordinator_ref.send_control(
                "builder",
                MessageType.UPDATES_ON_INVENTORY.value,
                {"progress": progress_list},
            )
            self.last_inventory_report = time.time()
            summary = ", ".join(f"{p['material']}:{p['completion_pct']}%" for p in progress_list)
            self.log.info(f"Progres enviat: {summary}")
        except Exception as e:
            self.log.error(f"Error enviant progres: {e}")

    def _switch_strategy(self, strategy_name: str | None) -> None:
        """Switch mining strategy."""
        if not strategy_name:
            self.mc.postToChat("[Miner] Error: cap nom d'estrategia proporcionat")
            return

        strategy = get_strategy(strategy_name)
        if strategy:
            self.current_strategy = strategy
            self.mc.postToChat(f"[Miner] Estrategia canviada a '{strategy_name}'")
            self.log.info(f"Estrategia canviada: {strategy_name}")
        else:
            available = ", ".join(list_strategies())
            self.mc.postToChat(f"[Miner] Error: estrategia desconeguda '{strategy_name}'")
            self.mc.postToChat(f"[Miner] Disponibles: {available}")

    def _show_strategies(self) -> None:
        """List available mining strategies."""
        available = ", ".join(list_strategies())
        current = self.current_strategy.get_name() if self.current_strategy else "none"
        self.mc.postToChat(f"[Miner] Estrategies: {available}")
        self.mc.postToChat(f"[Miner] Actual: {current}")

    def _report_status(self) -> None:
        """Report current miner status."""
        state = self.state_manager.state
        strategy = self.current_strategy.get_name() if self.current_strategy else "none"
        inv_str = ", ".join(f"{k}:{v}" for k, v in self.inventory.stock.items()) or "empty"

        self.mc.postToChat(f"[Miner] Estat: {state}, Estrategia: {strategy}")
        self.mc.postToChat(f"[Miner] Inventari: {inv_str}")

        if self.bom_request:
            mat = self.bom_request["material"]
            need = self.bom_request["amount"]
            have = self.inventory.available(mat)
            pct = int((have / need) * 100) if need > 0 else 0
            self.mc.postToChat(f"[Miner] Peticio: {mat} ({have}/{need}, {pct}%)")

        if self.mined_materials:
            mined_str = ", ".join(f"{k}:{v}" for k, v in self.mined_materials.items())
            self.mc.postToChat(f"[Miner] Materials minats: {mined_str}")

    def _is_bom_complete(self) -> bool:
        """
        Check if all BOM materials are satisfied in inventory.
        
        Returns:
            True if all BOM materials have required amounts, False otherwise
        """
        if not self.bom_request:
            return False
        
        for material, required in self.bom_request.items():
            have = self.inventory.available(material)
            if have < required:
                return False
        
        return True

    def _reset_state(self) -> None:
        """Reset miner state."""
        self.bom_request = None
        self.mining_coords = None
        self.last_inventory_report = 0.0

    def get_mined_summary(self) -> Dict[str, int]:
        """
        Get summary of all materials mined in current operation.
        
        Returns:
            Dict of {material_name: count}
        """
        return self.mined_materials.copy() if self.mined_materials else {}

    def clear_mined_summary(self) -> None:
        """Clear the mined materials tracking for next operation."""
        self.mined_materials.clear()

    # ======== Hooks ========

    def set_coordinator(self, coordinator):
        """Inject coordinator reference."""
        self._coordinator_ref = coordinator

    def on_start(self) -> None:
        pass

    def on_stop(self) -> None:
        self._reset_state()
