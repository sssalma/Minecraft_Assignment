from application.agent_state import AgentState
from messaging.message import Message

class Coordinator:
    """
    Coordina i controla el flujo entre agentes.
        -emite comandos de control
    """

    def __init__(self, bus):
        self.bus = bus
        self.agents = {}

    def register_agent(self, agent): #dona d'alta a un agent
        self.agents[agent.name] = agent

    def tick(self):
        for agent in self.agents.values():
            agent.run_step()

    def send_control(self, target: str, command: str):
        """
        Envia comandes de control (broadcast o a l'agent)
        """
        print("[Coordinator] Enviant control:", target, command)
        payload = {"command": command}

        if target == "ALL":
            for name in self.agents:
                self.bus.send(
                    Message(
                        source="Coordinator",
                        target=name,
                        msg_type="command.control",
                        payload=payload
                    )
                )
        else:
            self.bus.send(
                Message(
                    source="Coordinator",
                    target=target,
                    msg_type="command.control",
                    payload=payload
                )
            )