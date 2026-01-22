import pytest
from src.application.state_manager import StateManager
from src.application.agent_state import AgentState


def test_state_transition():
    sm = StateManager("TestAgent")
    sm.transition(AgentState.RUNNING, "start")
    assert sm.state == AgentState.RUNNING


class DummyObserver:
    def __init__(self):
        self.notifications = []

    def on_state_change(self, agent_name, new_state, reason):
        self.notifications.append((agent_name, new_state, reason))
def test_invalid_state_transition_does_not_change_state_nor_notify():
    sm = StateManager("TestAgent")
    observer = DummyObserver()
    sm.add_observer(observer)

    initial_state = sm.state

    # IDLE -> ERROR NO és permès segons ALLOWED_TRANSITIONS
    with pytest.raises(ValueError):
        sm.transition(AgentState.ERROR, "invalid transition")

    # 1️⃣ l’estat NO ha canviat
    assert sm.state == initial_state

    # 2️⃣ cap observer ha estat notificat
    assert observer.notifications == []
