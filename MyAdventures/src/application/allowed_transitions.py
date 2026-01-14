from ..messaging.enums.message_status import MessageStatus

ALLOWED_TRANSITIONS = {
    MessageStatus.IDLE: [
        MessageStatus.RUNNING,
        MessageStatus.STOPPED,
    ],
    MessageStatus.RUNNING: [
        MessageStatus.IDLE,
        MessageStatus.PAUSED,
        MessageStatus.WAITING,
        MessageStatus.ERROR,
        MessageStatus.STOPPED,
        MessageStatus.RUNNING,
    ],
    MessageStatus.PAUSED: [
        MessageStatus.RUNNING,
        MessageStatus.STOPPED,
    ],
    MessageStatus.WAITING: [
        MessageStatus.RUNNING,
        MessageStatus.ERROR,
        MessageStatus.STOPPED,
    ], 
    MessageStatus.ERROR: [
        MessageStatus.STOPPED,
    ],
    MessageStatus.STOPPED: [
        MessageStatus.IDLE,
        MessageStatus.RUNNING,
        MessageStatus.PAUSED,
    ],
}