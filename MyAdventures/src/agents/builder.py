from .agent_base import BaseAgent
from application.agent_state import AgentState
import time
from domain.map_data import MapData
from domain.bom import BOM, BOMPhase

class BuilderBot(BaseAgent):  ###builder de prova
    def __init__(self, mc,bus):
        super().__init__("BuilderBot", mc, bus)

        self.bom = None

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
                self.state_manager.transition(
                    AgentState.ERROR,
                    "material supply timeout"
                )
            return None
         # si estat=running i tinc BOM, seguent fase
        if self.state_manager.is_running() and self.bom:
            phase = self.bom.current_phase()
            if phase:
                return phase
            
        return None

    def act(self, action):
        if not isinstance(action, BOMPhase):
            return
        self.required_amount = action.amount
        self.current_inventory = 0


        self.send_message(
                target="MinerBot",
                msg_type="materials.requirements.v1",
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
 
    def on_message_received(self, msg):
        #rebo el mapa
        if msg.msg_type == "map.v1":
            try:
                map_data = MapData(**msg.payload)
            except TypeError:
                self.state_manager.transition(
                    AgentState.ERROR,
                    "map.v1 invalid"
                ) 
                return
            #genera el BOM
            self.bom = self.generate_bom(map_data)

            self.state_manager.transition(
                AgentState.RUNNING,
                "BOM generat a partir del mapa"
            )
        #rebo material
        elif msg.msg_type == "material.supply":
            self.current_inventory += msg.payload.get("amount", 0)
            self.last_material_time = time.time()

            if self.current_inventory >= self.required_amount:
                self.bom.advance()
                self.state_manager.transition(
                    AgentState.RUNNING,
                    "fase completada, avançant"
                )
    def generate_bom(self, map_data):
        flat_size = len(map_data.flat_region)

        phases = [
            BOMPhase("foundations", "stone", flat_size * 2),
            BOMPhase("walls", "stone", flat_size * 3),
            BOMPhase("roof", "wood", flat_size)
        ]
        return BOM(phases)
