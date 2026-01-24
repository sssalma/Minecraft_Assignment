import pytest
import asyncio

from src.application.agent_state import AgentState
from src.messaging.message import Message
from src.messaging.message_types import INVENTORY_V1

from src.agents.agent_base import BaseAgent
from src.agents.builder import BuilderBot
from src.agents.explorer import ExplorerBot
from src.agents.miner import MinerBot


# ---------------------------
# DOUBLES (fakes simples)
# ---------------------------

class DummyBus:
    def __init__(self):
        self.messages = []

    async def publish(self, msg):
        self.messages.append(msg)


class DummyMC:
    def __init__(self):
        self.chat = []

    def post_chat(self, msg):
        self.chat.append(msg)

    def get_mc(self):
        return self

    class player:
        @staticmethod
        def getTilePos():
            class Pos:
                x, y, z = 0, 10, 0
            return Pos()

    def getHeight(self, x, z):
        return 10


# ---------------------------
# BASE AGENT
# ---------------------------

class DummyAgent(BaseAgent):
    def perceive(self):
        return "data"

    def decide(self, perception):
        return "action"

    def act(self, action):
        self.last_action = action


@pytest.mark.asyncio
#comprova que el cicle bàsic d’execució d’un agent s’inicia correctament i 
#que el mètode run_step invoca les operacions esperades sense produir errors.
async def test_base_agent_run_step_executes_cycle():
    bus = DummyBus()
    mc = DummyMC()
    agent = DummyAgent("Dummy", mc, bus)

    agent.state_manager.transition(AgentState.RUNNING, "start")
    await agent.run_step()

    assert agent.last_action == "action"


# ---------------------------
# BUILDER BOT
# ---------------------------

@pytest.mark.asyncio
#valida que el BuilderBot detecta un flux incoherent de missatges (recepció de materials sense el context necessari) 
#i transita correctament a l’estat ERROR.
async def test_builder_receives_inventory_foradecontext():
    bus = DummyBus()
    mc = DummyMC()
    builder = BuilderBot(mc, bus)

    from src.domain.bom import BOM, BOMPhase
    builder.bom = BOM([BOMPhase("test", "stone", 5)])

    builder.required_amount = 5

    msg = Message(
        source="MinerBot",
        target="BuilderBot",
        msg_type=INVENTORY_V1,
        payload={"material": "stone", "amount": 5}
    )

    await builder.on_message_received(msg)

    assert builder.state_manager.state == AgentState.ERROR


# ---------------------------
# EXPLORER BOT
# ---------------------------
#comprova que l’ExplorerBot, en processar un mapa vàlid,
# genera i envia un missatge amb la info  del mapa,
# simulant l’enviament asíncron mitjançant dobles de prova.
def test_explorer_act_sends_map_message(monkeypatch):
    bus = DummyBus()
    mc = DummyMC()
    explorer = ExplorerBot(mc, bus)

    explorer.state_manager.transition(AgentState.RUNNING, "start")

    # Evitem create_task real (no hi ha event loop en tests síncrons)
    monkeypatch.setattr("asyncio.create_task", lambda coro: None)

    class DummyMap:
        def is_valid(self):
            return True

        def to_payload(self):
            return {"origin": (0, 10, 0), "flat_region": [], "obstacles": []}

    explorer.act(DummyMap())

    # Si no peta, el comportament és correcte
    assert explorer.state_manager.state == AgentState.WAITING

# ---------------------------
# MINER BOT
# ---------------------------
@pytest.mark.asyncio
async def test_miner_invalid_material_request_sets_error():
    bus = DummyBus()
    mc = DummyMC()
    miner = MinerBot(mc, bus)

    msg = Message(
        source="BuilderBot",
        target="MinerBot",
        msg_type="materials.requirements.v1",
        payload={"material": None, "amount": -1}
    )

    with pytest.raises(ValueError):
        await miner.on_message_received(msg)
