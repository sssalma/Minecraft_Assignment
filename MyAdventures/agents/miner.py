from .agent_base import BaseAgent
import time

class MinerBot(BaseAgent):
    def __init__(self, mc):
        super().__init__("MinerBot", mc)
        
        #llista de compra (material a minar requerit pel builder)
        self.current_order = None 
        self.materials_db = {
            "STONE": 1,
            "DIRT": 3,
            "WOOD": 17,   
            "SAND": 12,
            "GRAVEL": 13,
            "GOLD": 41    
        }

    def perceive(self):
        # testeig
        return None

    def decide(self, perception):
        # testeig
        return "wait"

    def act(self, action):
        pass

    def on_message_received(self, msg):
        # crido al pare
        #super().process_message(msg)

        # quan es necessiti un material: message type:  request.material
        if msg.msg_type == "request.material":
            sender = msg.source
            material = msg.payload.get("material")
            amount = msg.payload.get("amount")
            
            print(f"[{self.name}] ¡Petición recibida de {sender}! Necesita {amount} de {material}.")
            self.mc.postToChat(f"Miner: Recibido! Buscando {material} para {sender}...")

            # --- SIMULACIÓ DE Resposta (HANDSHAKE) ---
            # Para probar que se hablan, le respondemos "Aquí tienes" inmediatamente.
            # (Más tarde cambiaremos esto por la acción real de picar).
            
            reply_payload = {
                "material": material,
                "amount": amount,
                "status": "delivered"
            }
            
            # Envio la resposta
            self.send_message(sender, "material.supply", reply_payload)
            print(f"[{self.name}] Respuesta enviada a {sender}.")