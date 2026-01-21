import asyncio
import logging
from src.application.agent_state import AgentState




class AgentRunner:
    """
    Patró Active Object per controlar l'execució asíncrona d'un agent.
    Permet executar periòdicament run_step() respectant l'estat actual de cada agent.
    """

    def __init__(self, agent, tick_interval: float = 0.5):
        self.agent = agent
        self.tick_interval = tick_interval # Temps (en segons) entre cada tick
        self._running = False

    async def run(self):
        """
        Bucle principal del runner: tasca asíncrona.
        """
        self._running = True
        print(f"[Runner] Iniciat per {self.agent.name}")

        try:
            while self._running:
                state = self.agent.state_manager.state
                # STOP definitiu

                if state == AgentState.PAUSED:
                    await asyncio.sleep(self.tick_interval)
                    continue

                if state in (AgentState.STOPPED, AgentState.ERROR):
                    print(f"[Runner] {self.agent.name} finalitzat (state={state.value})")
                    break

                # Faré el run_step només quan l'estat sigui RUNNING o WAITING
                if state in (AgentState.RUNNING, AgentState.WAITING):
                    try:
                        self.agent.run_step()
                    except Exception as e:
                        print(f"[Runner] Error en {self.agent.name}: {e}")
                        self.agent.reset()
                        self.agent.state_manager.transition(
                            AgentState.ERROR,
                            f"exception in runner: {e}"
                        )
                        break

                # si es IDLE o PAUSED -> no executo la lògica
                await asyncio.sleep(self.tick_interval)

        except asyncio.CancelledError:
            print(f"[Runner] Cancel·lat {self.agent.name}")

        finally:
            self._running = False
            print(f"[Runner] Aturat {self.agent.name}")

    def stop(self):
        self._running = False
