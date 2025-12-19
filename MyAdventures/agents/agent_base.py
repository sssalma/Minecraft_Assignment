from abc import ABC, abstractmethod
import sys
import os

#importo mòduls de la carpeta superior
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from message_bus import MessageBus
from message import Message


class BaseAgent(ABC):
    """
    Classe base em defineix el cicle de vida de qualssevol agent.
    Patrons: Template Method + State Machine ; Pub/Sub pero conectar amb el MessageBus.
    """
    def __init__(self, name, mc):
        self.name = name
        self.mc = mc

        # Màquina d'estats: IDLE, RUNNING, PAUSED, WAITING, STOPPED, ERROR
        self.state = "IDLE" 

        # Subscripció al bus:
        self.bus = MessageBus()
        self.bus.register(self.name) # com a l'observer, cada agent s'autoinscriu a les notícies. (al Bus)



    def run_step(self):
        """
        Quan l'estat és RUNNING, s'executa a cada cicle del joc.
        """
        #buido la bústia
        incoming_messages = self.bus.receive(self.name)
        for msg in incoming_messages:
            self.process_message(msg)

        if self.state == "RUNNING":
            perception = self.perceive()
            action = self.decide(perception)
            self.act(action)


    def send_message(self, target, msg_type, payload):
        """Enviament de missatges JSON que es validen a MESSAGE.
            Envio el missatge sencer i .send(message) del bus ja veurà ququi es el target"""
        msg = Message(source=self.name, target=target, msg_type=msg_type, payload=payload)
        
        self.bus.send(msg)
        
        # Log de sortida per traçabilitat
        print(f"OUT [{self.name}] >> {msg_type} -> {target}")

    def process_message(self, msg):
        """Pel PROCESSAMENT dels missatges.(Comandes de control) """

        # Log d'entrada per traçabilitat
        print(f"IN  [{self.name}] << {msg.msg_type} de {msg.source}")
        
        # Canvia l'estat si son comandes de control: estats: IDLE,RUNNING PAUSED, WAITING,STOPPED,ERROR 
        if msg.msg_type == "command.control":
            cmd = msg.payload.get("command")
            if cmd == "pause": self.set_state("PAUSED")
            elif cmd == "resume": self.set_state("RUNNING")
            elif cmd == "stop": self.set_state("IDLE")

        #no vull que els fills estiguin cridant al pare (desacoblo amb un altre met)
        self.on_message_received(msg) 

    def on_message_received(self,msg):
        #per defecte no fa res (HOOK)

        pass
    def set_state(self, new_state):
        """Canvia l'estat i avisa."""
        print(f"[{self.name}] Canvi d'estat: {self.state} -> {new_state}")
        self.state = new_state

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