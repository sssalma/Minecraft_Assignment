
import threading
import asyncio
import logging

from src.minecraft.mc_client import MinecraftClient
from src.messaging.message_bus import MessageBus
from src.application.coordinator import Coordinator
from src.reflection.agent_loader import AgentLoader
from src.application.agent_state import AgentState
from src.runtime.workflow_observer import WorkflowObserver

log = logging.getLogger(__name__)


class Workflow(threading.Thread):
    """
   Cada workflow representa una instància/copia completa del sistema.
    aquí es on s'impelemnta l'asincronia "global" del sistema.
    per cada comanda que incii l'explorer, es crea un workflow nou.
    Amb instàncies pròpies de bus, coordinator i agents i del minecraftclient
    Així el bloqueig d'un agent boquejarà només el seu thread/workflow.
    id útil pels logs,comandes,i debug general.
    """

    def __init__(self, workflow_id:int):
        super().__init__(daemon=True)
        self.id = workflow_id
        self.mc = MinecraftClient()

        self.bus = None
        self.coordinator = None
        self.agents = []

        self._running = True

    def run(self):
        """Punt d'entrada del thread."""
        asyncio.run(self._run_async())

    async def _run_async(self):
        log.info(f"[Workflow {self.id}] Iniciant workflow")

        # Creo infrastructura + carrego agents del thread -> els registro al coordinador i 
        self.bus = MessageBus()
        self.coordinator = Coordinator(self.bus)
        loader = AgentLoader(self.bus)
        self.agents = loader.load(self.mc)
        for agent in self.agents:
            self.coordinator.register_agent(agent)
        #ja existeixen els agents-> els faig observers dels canvis d'estat
        self.observer = WorkflowObserver(self.id)
        for agent in self.agents:
            agent.state_manager.add_observer(self.observer)


        await self.coordinator.start()
        await self.coordinator.start_agents()

        # Llançar workflow (explorer start)
        self.coordinator.send_control("ExplorerBot", "start")

        # Loop de vida del workflow
        try:
            while self._running:
                await asyncio.sleep(0.5)
        finally:
            self.stop()

    def stop(self):
        """Demana l'aturada del workflow."""
        self._running = False

 