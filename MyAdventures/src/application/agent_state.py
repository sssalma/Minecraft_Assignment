from enum import Enum

class AgentState(Enum):
    
    #FSM = estats i transicions entre estats
    #Estats
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    WAITING = "WAITING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"

#Transicions entre estats
ALLOWED_TRANSITIONS = {
        AgentState.IDLE: {
            AgentState.RUNNING,
            AgentState.STOPPED
        },
        AgentState.RUNNING: {
            AgentState.PAUSED,
            AgentState.WAITING,
            AgentState.ERROR,
            AgentState.STOPPED
        },
        AgentState.PAUSED: {
            AgentState.RUNNING,
            AgentState.STOPPED
        },
        AgentState.WAITING: {
            AgentState.RUNNING,
            AgentState.ERROR,
            AgentState.STOPPED
        },
        AgentState.ERROR: {
            AgentState.STOPPED
        },
        AgentState.STOPPED: {
        AgentState.IDLE,
        AgentState.RUNNING,
        AgentState.PAUSED,  
    }
}
