from .agent_base import BaseAgent
from src.application.agent_state import AgentState
from src.domain.inventory import Inventory
from src.strategies.mining.vertical_mining import VerticalMining
from src.strategies.mining.grid_mining import GridMining
from src.strategies.mining.mining_interface import MiningStrategy
from src.strategies.mining.vein_mining import VeinMining
from src.messaging.message_types import INVENTORY_V1


class MinerBot(BaseAgent):
    def __init__(self, mc, bus):
        super().__init__("MinerBot", mc, bus)
        self.inventory = Inventory()

        # stock inicial testing
        #self.inventory.add("stone", 500)
        #self.inventory.add("wood", 200)

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

    async def on_message_received(self, msg):
        await super().on_message_received(msg)
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
        # EXECUCIÓ DE LA MINERIA VIA STRATEGY
        extracted = self.strategy.mine(self, amount)
        total_amount = sum(extracted.values()) #decisió de disseny:per simplicitat, només tinc en compte la quantitat.
        if total_amount <=0 :
            self.state_manager.transition(
                AgentState.ERROR,
                f"No s'ha pogut extreure {material}"
            )
            return    
        # RESPOSTA AL BUILDER

        self.send_message(
            target="BuilderBot",
            msg_type=INVENTORY_V1,
            payload={
                "material": "generic",
                "amount": total_amount
                }
            )
        self.state_manager.transition(
            AgentState.WAITING,
            "materials enviats"
            )
        
    def reset(self):
        self.strategy = VerticalMining()