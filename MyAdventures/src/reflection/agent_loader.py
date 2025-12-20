import os
import importlib
import inspect
from agents.agent_base import BaseAgent

class AgentLoader:
    def __init__(self, bus):
        self.bus = bus
    def load(self, mc_client):
        agents = []
        
        # es calcula el camí absolut a la carpeta agents per evitar problemes amb rutes relatives
        base_dir = os.path.dirname(os.path.dirname(__file__))
        agents_dir = os.path.join(base_dir, "agents")

        for filename in os.listdir(agents_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module = importlib.import_module(f"agents.{filename[:-3]}")

                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                        print("Classe trobada:", obj, "abstracta?", inspect.isabstract(obj))
                        agents.append(obj(mc_client,self.bus))

        return agents
