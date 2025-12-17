import json
import uuid
from datetime import datetime,timezone

class Message:
    """
    Missatge estandarditzat segons l'esquema JSON del projecte.
    Patró: Data Transfer Object (DTO) + Validator.
    """
    def __init__(self, source, target, msg_type, payload, context=None):
        self.source = source
        self.target = target
        self.msg_type = msg_type  
        self.payload = payload    
        self.timestamp = datetime.now(timezone.utc).isoformat() # pel format ISO 8601 
        self.status = "NEW"
        self.context = context or {}
        
        # quan creo el missatge, el valido
        self.validate()

    def validate(self):
        """Assegura que el missatge compleix els requisits tècnics."""
        if not self.source or not self.target:
            raise ValueError("Missatge sense origen o destí.")
        if not self.msg_type:
            raise ValueError("Missatge sense tipus.")
        if not isinstance(self.payload, dict):
            raise ValueError("Payload ha de ser un diccionari")

    def to_json(self):
        """Serialitza el missatge per enviar-lo o guardar-lo en logs."""
        return json.dumps({
            "type": self.msg_type,
            "source": self.source,
            "target": self.target,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "status": self.status,
            "context": self.context
        })

    def __str__(self):
        return f"[{self.timestamp}] {self.source} -> {self.target}: {self.msg_type}"