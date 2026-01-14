import logging
from ..messaging.enums.message_status import MessageStatus
from .allowed_transitions import ALLOWED_TRANSITIONS

log = logging.getLogger(__name__)

class StateManager:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.state = MessageStatus.IDLE

    def transition(self, new_state, reason=""):
        """Transiciona l'estat de l'agent validant que sigui permesa."""
        # Obtenir transicions permeses des de l'estat actual
        allowed = ALLOWED_TRANSITIONS[self.state]
        
        # Verificar si la transició és vàlida
        is_valid = False
        i = 0
        while i < len(allowed):
            if allowed[i] == new_state:
                is_valid = True
                break
            i = i + 1
        
        if not is_valid:
            # Transició invàlida - error
            log.error(
                f"[{self.agent_name}] Transició invàlida: {self.state.value} -> {new_state.value}")
            raise ValueError("Invalid state transition")

        # Guardar estat anterior
        prev = self.state
        # Actualitzar a nou estat
        self.state = new_state

        # Registrar transició
        log.info(
            f"[{self.agent_name}] STATE {prev.value} -> {new_state.value} | reason={reason}"
        )

    def is_running(self):
        """Retorna True si l'agent està en estat RUNNING."""
        running = False
        if self.state == MessageStatus.RUNNING:
            running = True
        return running
    
    def is_state(self, state):
        """Retorna True si l'agent està en l'estat especificat."""
        matches = False
        if self.state == state:
            matches = True
        return matches
