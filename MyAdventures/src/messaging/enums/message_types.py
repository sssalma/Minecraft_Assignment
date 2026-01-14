"""Message types enumeration."""
from enum import Enum


class MessageType(Enum):
    """Tipus de missatge segons l'esquema JSON del projecte."""
    
    UPDATES_ON_INVENTORY = "inventory.v1" # miner -> builder
    CONFIRM_COMPLETION_OF_BUILD = "build.v1" # builder -> all
    SEND_TERRAIN_DATA_MAP = "map.v1" # explorer -> builder
    
    START_MAIN_ACTION = "start" # coordinator -> agents
    PAUSE_AGENT = "pause" # coordinator -> agents
    RESUME_AGENT = "resume" # coordinator -> agents
    STOP_AGENT = "stop" # coordinator -> agents
    
    SHOW_AGENT_STATUS = "status" # coordinator -> agents   
    FULFILL_INVENTORY = "fulfill.bom" # coordinator -> miner
    BUILDER_SEND_BOM = "material.requirements.v1" # builder -> miner
    
    BUILDER_NEW_PLAN = "new.plan" # coordinator -> builder
    MINER_NEW_STRATEGY = "new.strategy" # coordinator -> miner
    EXPLORER_NEW_RANGE = "new.range" # coordinator -> explorer
    
    SHOW_BUILDER_PLANS = "show.plans" # coordinator -> builder
    SHOW_MINER_STRATEGIES = "show.strategies" # coordinator -> miner
    
    SHOW_STATUS = "show.status" # coordinator -> all agents
    
    HELP = "help" # coordinator -> any agents 

    def __str__(self):
        return self.value
