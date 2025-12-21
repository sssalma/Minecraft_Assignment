from .agent_base import BaseAgent
from application.agent_state import AgentState
from domain.inventory import Inventory
from strategies.mining.vertical_mining import VerticalMining
from strategies.mining.grid_mining import GridMining
from strategies.mining.mining_interface import MiningStrategy
from strategies.mining.vein_mining import VeinMining

import time

class MinerBot(BaseAgent):
    def __init__(self, mc, bus):
        super().__init__("MinerBot", mc, bus)
        self.inventory = Inventory()

        # stock inicial testing
        self.inventory.add("stone", 500)
        self.inventory.add("wood", 200)

        #mining vertical per default
        self.strategy: MiningStrategy = VerticalMining()
        
    def perceive(self):
        # testeig
        return None

    def decide(self, perception):
        # testeig
        return "wait"

    def act(self, action):
        pass

    def on_message_received(self, msg):

        # CANVI D'ESTRATÈGIA (runtime)

        if msg.msg_type == "command.strategy":
            strategy_name = msg.payload.get("name")
            
            if strategy_name == "vertical":
                self.strategy = VerticalMining()
                self.mc.post_chat("Miner: estratègia canviada a VERTICAL")

            elif strategy_name == "grid":
                self.strategy = GridMining()
                self.mc.post_chat("Miner: estratègia canviada a GRID")

            elif strategy_name == "vein":
                self.strategy = VeinMining()
                self.mc.post_chat("Miner: estratègia canviada a VEIN")

            else:
                self.mc.post_chat(f"Miner: estratègia desconeguda {strategy_name}, mantening l'actual")
            return
        
        
        # PETICIÓ DE MATERIALS

        if msg.msg_type != "materials.requirements.v1":
            return
        
        material = msg.payload.get("material")
        amount = msg.payload.get("amount")

        if not material or not isinstance(amount, int) or amount <= 0:
            self.state_manager.transition(
                AgentState.ERROR,
                "invalid material request"
            )
            return
        
        # EXECUCIÓ DE LA MINERIA

  
        self.state_manager.transition(
            AgentState.RUNNING,
            f"minant {amount} {material}"
        )

        supplied = self.strategy.mine(self, material, amount)
        if supplied <=0:
            self.state_manager.transition(
                AgentState.ERROR,
                f"No hi ha {material} disponible"
            )
            return
        

        # RESPOSTA AL BUILDER

        self.send_message(
            target="BuilderBot",
            msg_type="material.supply",
            payload={
                "material": material,
                "amount": supplied
                }
            )
        self.state_manager.transition(
            AgentState.STOPPED,
            "materials anviats"
            )
        
    def reset(self):
        self.strategy = VerticalMining()