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
        player_y = perception["pos"].y
        ground_y = perception["ground_y"]
        
        # Si está 3 bloques por encima del suelo, se considera 'flying'
        if player_y > ground_y + 3:
            return "volant"
        return "chill"

    def act(self, action):
        if action == "volant":
            self.mc.postToChat(f"[{self.name}] OMYGA estic volant!")
        elif action == "chill":
            pass