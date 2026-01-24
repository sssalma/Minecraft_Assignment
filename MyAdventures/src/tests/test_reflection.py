import pytest
import types

from src.reflection.agent_loader import AgentLoader
from src.agents.agent_base import BaseAgent


# ---------------------------
# DOUBLES
# ---------------------------

class DummyBus:
    pass


class DummyMC:
    pass


class FakeAgent(BaseAgent):
    def __init__(self, mc_client, bus):
        super().__init__("FakeAgent", mc_client, bus)

    def perceive(self): 
        pass

    def decide(self, p): 
        pass

    def act(self, a): 
        pass

class NotAnAgent:
    pass


# ---------------------------
# TESTS
# ---------------------------

def test_agent_loader_loads_valid_agents(monkeypatch):
    """
    Comprova que l'AgentLoader carrega correctament
    les classes que hereten de BaseAgent i ignora la resta.
    """
    fake_module = types.SimpleNamespace(
        FakeAgent=FakeAgent,
        NotAnAgent=NotAnAgent
    )

    # simulem fitxers a la carpeta agents
    monkeypatch.setattr("os.listdir", lambda _: ["fake_agent.py"])
    monkeypatch.setattr(
        "importlib.import_module",
        lambda _: fake_module
    )

    loader = AgentLoader(DummyBus())
    agents = loader.load(DummyMC())

    assert len(agents) == 1
    assert isinstance(agents[0], FakeAgent)


def test_agent_loader_returns_empty_list_when_no_agents(monkeypatch):
    """
    Comprova que l'AgentLoader retorna una llista buida
    quan no es troben agents vàlids.
    """
    fake_module = types.SimpleNamespace()

    monkeypatch.setattr("os.listdir", lambda _: ["empty.py"])
    monkeypatch.setattr(
        "importlib.import_module",
        lambda _: fake_module
    )

    loader = AgentLoader(DummyBus())
    agents = loader.load(DummyMC())

    assert agents == []
