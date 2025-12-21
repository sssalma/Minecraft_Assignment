from .agent_base import BaseAgent
from application.agent_state import AgentState
from domain.map_data import MapData


class ExplorerBot(BaseAgent):

    #crido al constructor del pare
    def __init__(self, mc, bus): 
        super().__init__("ExplorerBot", mc, bus)
        self.failed_searches = 0

        self.MAX_SEARCH_ATTEMPTS = 20 #timeout

    #ubico al jugador: pos getTilePos())
    def perceive(self):
        try:
            mc = self.mc.get_mc()
            pos = mc.player.getTilePos()
            map_data = self.analyze_terrain((pos.x, pos.y, pos.z))
            return map_data
        except Exception as e:
            self.reset()
            self.state_manager.transition(
                AgentState.ERROR,
                f"no s'ha pogut analitzar el terreny: {e}"
            )
            return None
            
    #decideix si hia ha zona valida
    def decide(self, perception):
        if perception is None:
            return None

        if not self.state_manager.is_running():
            return None

        if not perception.is_valid():
            self.failed_searches += 1
            if self.failed_searches >= self.MAX_SEARCH_ATTEMPTS:
                self.reset()
                self.state_manager.transition(
                    AgentState.ERROR,
                    "no es troba area plana per construir"
                )
            return None
    # Zona válida trobada
        self.failed_searches = 0
        return perception


    def act(self, action):
        
        if not action:
            return
        self.mc.post_chat("Explorer: mapa enviat al Builder")
        self.send_message(
            target="BuilderBot",
            msg_type="map.v1",
            payload=action.to_payload()
        )

        self.state_manager.transition(
        AgentState.WAITING,
        "esperant nova ordre"
)

    
    def analyze_terrain(self, origin):
        elevation_map = {}
        flat_region = []
        obstacles = []

        #coordenades d'origen
        mc = self.mc.get_mc()
        ox, oy, oz = origin

        # exploració en un radi petit
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                x = ox + dx
                z = oz + dz
                y = mc.getHeight(x, z)
                elevation_map[(x, z)] = y # regió plana simple: mateixa altura que origen
                if y == oy:
                    flat_region.append((x, y, z))
                else:
                    obstacles.append((x, y, z))

        return MapData(
            origin=(ox, oy, oz),
            elevation_map=elevation_map,
            flat_region=flat_region,
            obstacles=obstacles
    )

    def reset(self):
        self.failed_searches = 0