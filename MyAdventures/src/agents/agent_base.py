from abc import ABC, abstractmethod
import sys
import os


from application.state_manager import StateManager
from application.agent_state import AgentState
import logging
log = logging.getLogger(__name__)
from messaging.message import Message


class BaseAgent(ABC):
    """
    Classe base em defineix el cicle de vida de qualssevol agent.
    Patrons: Template Method + State Machine ; Pub/Sub pero conectar amb el MessageBus.
    """
    def __init__(self, name, mc, bus):
        self.name = name
        self.mc = mc
        self.bus=bus

        self.state_manager = StateManager(self.name) 
        self.bus.register(self.name) # cada agent s'autoinscriu al Bus (pub/sub)



    def run_step(self):
        """
        Quan l'estat és RUNNING, s'executa a cada cicle del joc.
        """

        #print(f"[TICK] {self.name} estat={self.state_manager.state}")
        #buido la bústia
        incoming_messages = self.bus.receive(self.name)
        for msg in incoming_messages:
            self.process_message(msg)

        if self.state_manager.is_running():
            perception = self.perceive()
            action = self.decide(perception)
            self.act(action)


    def send_message(self, target, msg_type, payload):
        """Enviament de missatges JSON que es validen a MESSAGE.
            Envio el missatge sencer i .send(message) del bus ja veurà ququi es el target"""
        msg = Message(source=self.name, target=target, msg_type=msg_type, payload=payload)
        
        self.bus.send(msg)
        
        # Log de sortida per traçabilitat
        log.info(f"OUT [{self.name}] >> {msg_type} -> {target}")

    def process_message(self, msg):
        """Pel PROCESSAMENT dels missatges.(Comandes de control) """

        # Log d'entrada per traçabilitat
        log.info(f"IN  [{self.name}] << {msg.msg_type} de {msg.source}")
        
        # Canvia l'estat si son comandes de control: estats: IDLE,RUNNING PAUSED, WAITING,STOPPED,ERROR 
        # === Comandos de control ===
        if msg.msg_type == "command.control":
            cmd = msg.payload.get("command")

            if cmd == "start":
            # Solo arrancar si está idle o waiting
                if self.state_manager.is_state(AgentState.IDLE) or self.state_manager.is_state(AgentState.WAITING):
                    self.state_manager.transition(
                        AgentState.RUNNING,
                        "start command"
                        )

            elif cmd == "pause":
            # Solo se puede pausar si está ejecutando
                if self.state_manager.is_running():
                    self.state_manager.transition(
                        AgentState.PAUSED,
                        "pause command"
                    )

            elif cmd == "resume":
            # Solo se puede reanudar desde PAUSED
                if self.state_manager.is_state(AgentState.PAUSED):
                    self.state_manager.transition(
                        AgentState.RUNNING,
                        "resume command"
                    )

            elif cmd == "stop":
                # Stop siempre es seguro
                self.reset() #faig resett
                if not self.state_manager.is_state(AgentState.STOPPED):
                    self.state_manager.transition(
                        AgentState.STOPPED,
                        "stop command"
                    )
                    
        # IMPORTANTE: los comandos de control NO se propagan a los hijos
            return
        # === Mensajes de dominio ===
        self.on_message_received(msg)
    def on_message_received(self,msg):
        #per defecte no fa res (HOOK)

        pass
    
    #mètode per fer reset quan state = error
    def reset(self):
        pass

    # mètodes abstractes pels overrides dels fills ---
    @abstractmethod
    def perceive(self):
        pass

    @abstractmethod
    def decide(self, perception):
        pass

    @abstractmethod
    def act(self, action):
        pass
    
   