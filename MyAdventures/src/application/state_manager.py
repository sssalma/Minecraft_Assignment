import logging
from .agent_state import AgentState, ALLOWED_TRANSITIONS

log = logging.getLogger(__name__)

class StateManager:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.state = AgentState.IDLE

    def transition(self, new_state: AgentState, reason: str = ""):
        if new_state not in ALLOWED_TRANSITIONS[self.state]:
            log.error(
                f"[{self.agent_name}] Invalid transition:  {self.state.value} -> {new_state.value}")
            raise ValueError("Invalid state transition")

        prev = self.state
        self.state = new_state

        log.info(
            f"[{self.agent_name}] STATE {prev.value} -> {new_state.value} | reason={reason}"
        )

    def is_running(self)-> bool:
        return self.state == AgentState.RUNNING
    def is_state(self, state):
        return self.state == state
