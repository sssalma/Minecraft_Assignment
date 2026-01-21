from abc import ABC, abstractmethod

class StateObserver(ABC):

    @abstractmethod
    def on_state_change(self, agent_name, new_state, reason):
        pass
