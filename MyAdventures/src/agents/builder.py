from .agent_base import BaseAgent
from src.application.agent_state import AgentState
import time
from src.domain.inventory import Inventory
from src.domain.map_data import MapData
from src.domain.bom import BOM, BOMPhase
from src.construction.planners.build_planner import BuildPlanner
from src.construction.executors.build_executor import BuildExecutor
from src.messaging.message_types import *

class BuilderBot(BaseAgent):  ###builder de en el mon real
    def __init__(self, mc,bus):
        super().__init__("BuilderBot", mc, bus)

        self.bom = None
        self.map_data=None
        self.inventory = Inventory()
        self.required_amount = 0
        self.current_inventory = 0
        self.last_material_time = 0
        
        self.TIMEOUT_LIMIT = 20

    def perceive(self): 
        return None

    def decide(self, perception):
         # timeout esperant materials
        if self.state_manager.is_state(AgentState.WAITING):
            if time.time() - self.last_material_time > self.TIMEOUT_LIMIT:
                self.reset()
                self.state_manager.transition(
                    AgentState.ERROR,
                    "material supply timeout"
                )
            return None
         # si estat=running i tinc BOM, seguent fase
        if self.state_manager.is_running() and self.bom:
            phase = self.bom.current_phase()
            if phase is None: 
                    return None
            return phase
            
        return None

    def act(self, action):
        if not isinstance(action, BOMPhase):
            return
        self.required_amount = action.amount
        self.current_inventory = 0


        self.send_message(
                target="MinerBot",
                msg_type=MATERIAL_REQUIREMENTS_V1,
                payload={
                    "material": action.material,
                    "amount": action.amount
                }
            )
        self.last_material_time = time.time()
        self.state_manager.transition(
                AgentState.WAITING,
                "materials demanats al miner"
            )
 
    async def on_message_received(self, msg):
        #rebo el mapa
        if msg.msg_type == "map.v1":
            try:
                self.map_data = MapData(**msg.payload)
            except TypeError:
                self.reset()
                self.state_manager.transition(
                    AgentState.ERROR,
                    "map.v1 invalid"
                ) 
                return
            #genera el BOM
            self.bom = self.generate_bom(self.map_data)

            self.state_manager.transition(
                AgentState.RUNNING,
                "generant BOM a partir del mapa"
            )
        #rebo material
        elif msg.msg_type == INVENTORY_V1: 
            amount = msg.payload.get("amount", 0)
            material = msg.payload.get("material")

            self.inventory.add(material, amount)
            self.current_inventory += amount
            self.last_material_time = time.time()

            if self.current_inventory >= self.required_amount:
                self.bom.advance()

                if self.bom.current_phase() is None:
                    self.state_manager.transition(
                    AgentState.RUNNING,
                    "construint"
                )
                    self.start_construction()
                    return

                self.state_manager.transition(
                    AgentState.RUNNING,
                    "fase completada, avansant"
                )

    def generate_bom(self, map_data): 
        #decisions de disseny: per tenir 2 opcions de construccio en funcio del terreny pla
        flat_size = len(map_data.flat_region)
        if flat_size <10:
            phases = [
                BOMPhase("foundations", "stone", 2),
                BOMPhase("walls", "stone", 3),
                BOMPhase("roof", "wood", 1)
            ]
        else: 
            phases = [
                BOMPhase("foundations", "stone", 4),
                BOMPhase("walls", "wood", 6),
                BOMPhase("roof", "wood", 2)
            ]

        return BOM(phases)
    

    def start_construction(self):
        try:
            planner = BuildPlanner(self.map_data, self.bom)
            build_plan = planner.create_plan()

            executor = BuildExecutor(self.mc, self.inventory)
            executor.execute(build_plan)

            self.mc.post_chat("Builder: s'han construit totes les fases")

            self.state_manager.transition(
                AgentState.WAITING,
                "Fi construccio"
            )

        except Exception as e:
            self.reset()
            self.state_manager.transition(
                AgentState.ERROR,
                f"Error durant la construccio: {e}"
        )

    def reset(self):
        self.bom= None
        self.current_invetory= 0
        self.map_data= None
        self.required_amount=None