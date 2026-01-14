"""Classe base d'agent amb cicle percepció-decisió-acció."""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
from ..messaging.message import Message
from ..messaging.enums.message_status import MessageStatus
from ..application.state_manager import StateManager


class BaseAgent(ABC):
    """
    Classe base per tots els agents del sistema.
    Implementa el patró Percepció-Decisió-Acció.
    """

    def __init__(self, name, mc_client):
        """
        Inicialitza l'agent.
        
        Args:
            name: Nom únic de l'agent
            mc_client: Client de Minecraft per interactuar amb el món
        """
        self.name = name
        self.mc = mc_client
        self.state_manager = StateManager(name)
        self.log = logging.getLogger(f"Agent.{name}")
        
        # Cua de missatges pendents (per processar al tick)
        self.message_queue = list()

    # ======== Handler del MessageBus (async/push) ========

    async def handle_message(self, message):
        """
        Handler cridat pel MessageBus quan arriba un missatge.
        Encua el missatge per processar-lo al següent tick.
        
        Args:
            message: Missatge rebut del bus
        """
        # Registrar recepció del missatge
        self.log.info(f"Missatge rebut: {message.message_type} de {message.source}")
        
        # Afegir missatge a la cua
        self.message_queue.append(message)

    # ======== Cicle Percepció-Decisió-Acció (sync/tick) ========

    def run_step(self):
        """
        Executa un cicle complet de l'agent (cridat des del Coordinator.tick()).
        
        1. Processa missatges de la cua
        2. Si està RUNNING, executa perceive -> decide -> act
        """
        # 1. Processa missatges pendents
        queue_length = len(self.message_queue)
        
        while queue_length > 0:
            # Extreure primer missatge de la cua
            msg = self.message_queue.pop(0)
            
            try:
                # Processar missatge
                self.process_message(msg)
            except Exception as e:
                self.log.error(f"Error processant missatge: {e}")
            
            # Actualitzar longitud de la cua
            queue_length = len(self.message_queue)

        # 2. Cicle autònom (només si està actiu)
        is_running = self.state_manager.is_running()
        
        if is_running:
            try:
                # Fase de percepció
                perception = self.perceive()
                
                # Fase de decisió
                action = self.decide(perception)
                
                # Fase d'acció
                self.act(action)
            except Exception as e:
                self.log.error(f"Error al cicle P-D-A: {e}")
                self.state_manager.transition(MessageStatus.ERROR, str(e))

    @abstractmethod
    def process_message(self, message):
        """
        Processa un missatge rebut (implementat per cada agent).
        Aquesta funció maneja comandes com START, PAUSE, STOP, etc.
        
        Args:
            message: Missatge a processar
        """
        pass

    @abstractmethod
    def perceive(self):
        """
        Percepció: obté informació de l'entorn.
        
        Returns:
            Diccionari amb dades percebudes
        """
        pass

    @abstractmethod
    def decide(self, perception):
        """
        Decisió: analitza la percepció i decideix una acció.
        
        Args:
            perception: Dades de l'entorn
            
        Returns:
            Diccionari amb l'acció a executar
        """
        pass

    @abstractmethod
    def act(self, action):
        """
        Acció: executa l'acció decidida al món de Minecraft.
        
        Args:
            action: Acció a executar
        """
        pass

    # ======== Control d'estat ========

    def start(self, reason="Comanda rebuda"):
        """Inicia l'execució de l'agent."""
        self.state_manager.transition(MessageStatus.RUNNING, reason)
        self.on_start()

    def pause(self, reason="Comanda rebuda"):
        """Pausa l'agent."""
        self.state_manager.transition(MessageStatus.PAUSED, reason)
        self.on_pause()

    def stop(self, reason="Comanda rebuda"):
        """Atura l'agent."""
        self.state_manager.transition(MessageStatus.STOPPED, reason)
        self.on_stop()

    # Hooks opcionals (sobreescriure si cal)
    def on_start(self):
        """Cridat quan l'agent s'inicia."""
        pass

    def on_pause(self):
        """Cridat quan l'agent es pausa."""
        pass

    def on_stop(self):
        """Cridat quan l'agent s'atura."""
        pass
