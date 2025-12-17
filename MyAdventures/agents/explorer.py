from .agent_base import BaseAgent

class ExplorerBot(BaseAgent):

    #crido al constructor del pare
    def __init__(self, mc): 
        super().__init__("ExplorerBot", mc)

    #ubico al jugador: pos (getTilePos())+ alçada getHeight(pos.x, pos.z))
    def perceive(self):
        pos = self.mc.player.getTilePos()
        ground_height = self.mc.getHeight(pos.x, pos.z)
        return {"pos": pos, "ground_y": ground_height}

    #decideix si está elevat del terra
    def decide(self, perception):
        if not perception: return None 
        # Si estoy en el suelo, envío un mensaje de "Mapa Encontrado"
        if perception["pos"].y == perception["ground_y"]+1:
            return "publish_map"
        return "wait"


    def act(self, action):
        if action == "publish_map":
            # SIMULACRE!!!!!!!!!!!!!!!!!!!!!!! envio un JSON al bus
            payload = {
                "coordinates": {"x": 100, "z": 200},
                "status": "flat",
                "area_size": 10
            }
            # Enviamos a "ALL" (Broadcast) o a "BuilderBot"
            # Usamos send_message que hereda de BaseAgent
            self.send_message("BuilderBot", "map.v1", payload)
            #AUTODESCONEXIÓ per TESTEIGGGGGG -> canvi d'estat
            self.mc.postToChat("Explorer: Mapa enviatt. Letsgobabygirl.")
            self.set_state("IDLE")