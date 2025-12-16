from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Classe base em defineix el cicle de vida de qualssevol agent.
    Patrons: Template Method + State Machine.
    """
    def __init__(self, name, mc):
        self.name = name
        self.mc = mc
        # Màquina d'estats: IDLE, RUNNING, PAUSED, WAITING, STOPPED, ERROR
        self.state = "IDLE" 

    def run_step(self):
        """
        Este método se llama en cada ciclo del bucle principal (Game Loop).
        Solo actúa si el agente está despierto (RUNNING).
        """
        if self.state == "RUNNING":
            perception = self.perceive()
            action = self.decide(perception)
            self.act(action)

    def set_state(self, new_state):
        """Canvia l'estat i avisa."""
        print(f"[{self.name}] Canvi d'estat: {self.state} -> {new_state}")
        self.state = new_state

    # mètodes abstractes pels overrides dels fills ---
    @abstractmethod
    def perceive(self):
        pass

    @abstractmethod
    def decide(self, perception):
        pass

    @abstractmethod
    def act(self, action):
        pass