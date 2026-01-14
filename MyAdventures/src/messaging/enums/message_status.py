"""Message status enumeration."""
from enum import Enum


class MessageStatus(Enum):
    """Estat del missatge al llarg del seu cicle de vida."""
    NEW = "NEW"
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    WAITING = "WAITING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"

    def __str__(self):
        return self.value
