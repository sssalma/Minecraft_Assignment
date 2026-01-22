from src.messaging.message import Message
import asyncio
from src.runtime.agent_runner import AgentRunner

class Coordinator:
    """
    Coordina i controla el flux entre agents.
    Patró: Facade
    """

    def __init__(self, bus):
        self.bus = bus                 # Infraestructura asíncrona
        self.agents = {}               # Agents registrats
        self.runners = {}              # Active Objects dels agents
        self.bus_task = None           # Tasca async del MessageBus

    def register_agent(self, agent):
        """
        Dona d'alta un agent al sistema.
        """
        has_name = hasattr(agent, 'name')
        if not has_name:
            raise ValueError(f"Agent no té atribut 'name'")
        
        # Obtinc l'agent: el guardo al registre i en creo que runner
        name = agent.name
        self.agents[name] = agent
        self.bus.subscribe(name, agent.process_message) #!!!! subscric al bus
        runner = AgentRunner(agent)
        self.runners[name] = runner
        print(f"[Coordinator] Agent '{name}' registrat")

    async def start(self):
        """Inicia el bus de missatges en background."""
        # Verificar si ja hi ha una tasca activa
        task_exists = False
        if self.bus_task is not None:
            task_exists = True
        
        if not task_exists:
            # Crear tasca asincrònica per executar el bus
            self.bus_task = asyncio.create_task(self.bus.run())
            print("[Coordinator] Sistema iniciat")

    async def stop(self):
        """Atura el bus i tots els agents."""
        await self.bus.stop()
        task_exists = False
        if self.bus_task is not None:
            task_exists = True
        
        if task_exists:
            self.bus_task.cancel()            
            try:
                # Esperar que la tasca es cancel·li
                await self.bus_task
            except asyncio.CancelledError:
                pass    
        print("[Coordinator] Sistema aturat")


    
    async def start_agents(self):
        """
        Arrenca tots els agents com a tasques asíncrones.
        """
        for runner in self.runners.values():
            asyncio.create_task(runner.run())

        print("[Coordinator] Agents iniciats")

    async def stop_agents(self):
        """
        Atura tots els agents.
        """
        for runner in self.runners.values():
            runner.stop()

        print("[Coordinator] Agents aturats")  

    
    # ========= COMANDES DE CONTROL =========

    def send_control(self, target: str, command: str, payload= None):
        """
        Envia una comanda de control a un agent.
        Exemples: start, pause, resume, stop
        """
        print("[Coordinator] Enviant control:", target, command)
        message = Message(
                source="Coordinator",
                target=target,
                msg_type="command.control",
                payload={
                    "command": command,
                    "params": payload or {}
        }
            )
        self.bus.message_queue.put_nowait(message)

    # ========= CANVI D'ESTRATÈGIA =========

    def send_strategy(self, target: str, strategy_name: str):
        """
        Envia una comanda de canvi d'estratègia al MinerBot.
        """
        print("[Coordinator] Enviant strategy:", strategy_name)

        message = Message(
            source="Coordinator",
            target=target,
            msg_type="command.strategy",
            payload={"name": strategy_name}
        )

        self.bus.message_queue.put_nowait(message)
