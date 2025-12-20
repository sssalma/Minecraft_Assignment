from .agent_base import BaseAgent
from application.agent_state import AgentState
from domain.inventory import Inventory

import time

class MinerBot(BaseAgent):
    def __init__(self, mc, bus):
        super().__init__("MinerBot", mc, bus)
        self.inventory = Inventory()

        # stock inicial testing
        self.inventory.add("stone", 500)
        self.inventory.add("wood", 200)
        
    def perceive(self):
        # testeig
        return None

    def decide(self, perception):
        # testeig
        return "wait"

    def act(self, action):
        pass

    def on_message_received(self, msg):

        if msg.msg_type == "materials.requirements.v1":
            material = msg.payload.get("material")
            amount = msg.payload.get("amount")

        if not material or not isinstance(amount, int) or amount <= 0:
            self.state_manager.transition(
                AgentState.ERROR,
                "invalid material request"
    )
            return

        self.state_manager.transition(
            AgentState.RUNNING,
            f"minant {amount} {material}"
        )

        time.sleep(1) #testeig mineria
        available = self.inventory.available(material)
        if available <= 0:
                self.state_manager.transition(
                    AgentState.ERROR,
                    f"no hi ha {material} a l'inventari"
                )
                return
        supplied = min(available, amount)
        self.inventory.consume(material, supplied)
       
            # Envio la resposta
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