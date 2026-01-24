import pytest
import json
from src.messaging.message import Message
from src.messaging.validator import MessageValidator
from src.messaging.message_types import COMMAND_CONTROL_V1
#test per MESSAGE + VALIDATOR

def test_message_creation_valid():
    msg = Message(
        source="AgentA",
        target="AgentB",
        msg_type=COMMAND_CONTROL_V1,
        payload={"command": "start"}
    )

    assert msg.source == "AgentA"
    assert msg.target == "AgentB"
    assert msg.msg_type == COMMAND_CONTROL_V1
    assert isinstance(msg.payload, dict)
    assert msg.status == "NEW"

def test_message_invalid_payload_raises():
    with pytest.raises(ValueError):
        Message(
            source="AgentA",
            target="AgentB",
            msg_type=COMMAND_CONTROL_V1,
            payload="NOT_A_DICT"
        )

def test_validator_rejects_missing_target():
    msg = Message(
        source="AgentA",
        target="AgentB",
        msg_type=COMMAND_CONTROL_V1,
        payload={"command": "start"}
    )
    msg.target = None # Manipulo per fer-lo invàlid

    with pytest.raises(ValueError):
        MessageValidator.validate(msg)
def test_validator_rejects_missing_type():
    msg = Message(
        source="AgentA",
        target="AgentB",
        msg_type=COMMAND_CONTROL_V1,
        payload={}
    )

    msg.msg_type = None # Manipulo per fer-lo invàlid

    with pytest.raises(ValueError):
        MessageValidator.validate(msg)


def test_message_to_json():
    msg = Message(
        source="A",
        target="B",
        msg_type="test.type",
        payload={"x": 1}
    )

    data = json.loads(msg.to_json())

    assert data["source"] == "A"
    assert data["target"] == "B"
    assert data["type"] == "test.type"
    assert data["payload"] == {"x": 1}
    
def test_validator_rejects_non_dict_payload():
    msg = Message(
        source="AgentA",
        target="AgentB",
        msg_type=COMMAND_CONTROL_V1,
        payload={"ok": True}
    )

    msg.payload = "INVALID"

    with pytest.raises(ValueError):
        MessageValidator.validate(msg)
