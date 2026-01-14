import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from .enums import MessageStatus

class Message:
    """
    Missatge estandarditzat segons l'esquema JSON del projecte.
    Patró: Data Transfer Object (DTO) + Validator.
    """
    def __init__(self, source, target, message_type, payload=None, context=None):
        self.source = source
        self.target = target
        self.message_type = message_type
        
        # Convertir None a diccionari buit
        if payload is None:
            self.payload = {}
        else:
            self.payload = payload
            
        # Generar timestamp en format ISO 8601
        current_time = datetime.now(timezone.utc)
        self.timestamp = current_time.isoformat()
        
        # Estat inicial del missatge
        self.status = MessageStatus.NEW
        
        # Context addicional
        if context is None:
            self.context = {}
        else:
            self.context = context
        
        # Validar missatge abans de retornar
        self.validate()

    def validate(self):
        """Assegura que el missatge compleix els requisits tècnics."""
        # Verificar existència de source
        source_valid = False
        if self.source:
            source_valid = True
        
        # Verificar existència de target  
        target_valid = False
        if self.target:
            target_valid = True
        
        # Fallar si falta origen o destí
        if not source_valid or not target_valid:
            raise ValueError("Missatge sense origen o destí.")
        
        # Verificar existència de message_type
        type_valid = False
        if self.message_type:
            type_valid = True
        
        if not type_valid:
            raise ValueError("Missatge sense tipus.")
        
        # Verificar que payload és diccionari
        payload_is_dict = isinstance(self.payload, dict)
        if not payload_is_dict:
            raise ValueError("Payload ha de ser un diccionari")

    def to_json(self):
        """Serialitza el missatge per enviar-lo o guardar-lo en logs."""
        return json.dumps({
            "type": self.message_type,
            "source": self.source,
            "target": self.target,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "status": self.status.value,
            "context": self.context
        })

    def __str__(self):
        return f"[{self.timestamp}] {self.source} -> {self.target}: {self.message_type}"