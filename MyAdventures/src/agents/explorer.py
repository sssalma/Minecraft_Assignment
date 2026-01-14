"""Explorer agent implementation."""
from typing import Dict, Any
import asyncio
from .base_agent import BaseAgent
from domain.map_data import MapData
from ..messaging.message import Message
from ..messaging.enums.message_status import MessageStatus
from ..messaging.enums.message_types import MessageType


class ExplorerAgent(BaseAgent):
    """
    Agent encarregat d'explorar el terreny i generar mapes per al Builder.
    """

    def __init__(self, mc_client):
        super().__init__("explorer", mc_client)
        
        # Configuracio d'exploracio
        self.MAX_SEARCH_ATTEMPTS = 20  # timeout
        self.MAX_SEARCH_RANGE = 20
        self.default_range = 5
        
        # Estat intern
        self.failed_searches = 0
        self.temporal_coords = None
        self.temporal_range = None
        self.current_map_data = None
        self.exploration_complete = False
        self.coordinator = None  # S'assignarà després
        self.pending_request = None  # Guarda start pendents quan ja està executant

    # ======== Processament de missatges ========

    def process_message(self, message: Message) -> None:
        """
        Processa missatges rebuts del MessageBus.
        """
        msg_type = message.message_type

        # Comandes de control d'estat
        if msg_type == MessageType.START_MAIN_ACTION.value:
            payload = message.payload if isinstance(message.payload, dict) else {}

            # Si estem en execucio i no s'ha completat, decidir si interrompre o encuar
            if self.state_manager.state == MessageStatus.RUNNING and not self.exploration_complete:
                mode = payload.get("mode", "queue")  # per defecte, encuar
                if mode == "interrupt":
                    self.log.info("Interrompent exploracio actual i reiniciant amb nous parametres")
                    self._apply_start_payload(payload)
                    self.state_manager.transition(MessageStatus.RUNNING, "Reiniciat per interrupcio")
                    self.mc.postToChat("[Explorer] Exploracio interrompuda i reiniciada amb nous parametres")
                else:
                    self.pending_request = payload
                    self.mc.postToChat("[Explorer] Peticio START encuada; es processara en acabar l'actual")
                    self.log.info(f"Peticio encuada: {payload}")
                return

            # Cas normal: aplicar paràmetres i començar
            self._apply_start_payload(payload)
            self.state_manager.transition(MessageStatus.RUNNING, "Iniciant exploracio")
            self.mc.postToChat("[Explorer] Iniciant exploracio...")
            
        elif msg_type == MessageType.PAUSE_AGENT.value:
            self.state_manager.transition(MessageStatus.PAUSED, "Exploracio pausada")
            self.mc.postToChat("[Explorer] Pausat")
            
        elif msg_type == MessageType.RESUME_AGENT.value:
            self.state_manager.transition(MessageStatus.RUNNING, "Exploracio represa")
            self.mc.postToChat("[Explorer] Repres")
            
        elif msg_type == MessageType.STOP_AGENT.value:
            self.state_manager.transition(MessageStatus.STOPPED, "Exploracio aturada")
            self.exploration_complete = False
            self.temporal_coords = None
            self.temporal_range = None
            self.mc.postToChat("[Explorer] Aturat")

        # Configuracio de rang
        elif msg_type == MessageType.EXPLORER_NEW_RANGE.value:
            payload = message.payload if isinstance(message.payload, dict) else {}
            if "range" in payload:
                self.temporal_range = int(payload["range"])
                self.log.info(f"Nou rang temporal: {self.temporal_range}")
            if "x" in payload and "z" in payload:
                x = int(payload["x"])
                z = int(payload["z"])
                y = self.mc.getHeight(x, z)
                self.temporal_coords = (x, y, z)
                self.log.info(f"Noves coordenades temporals: {self.temporal_coords}")

        # Status
        elif msg_type == MessageType.SHOW_STATUS.value:
            self.log.info(f"Estat: {self.state_manager.state}")
            self.log.info(f"Rang: {self.temporal_range or self.default_range}")
            self.log.info(f"Intentos fallits: {self.failed_searches}/{self.MAX_SEARCH_ATTEMPTS}")
            if self.current_map_data:
                self.mc.postToChat(f"[Explorer] {self.current_map_data}")

        else:
            self.log.warning(f"Missatge no reconegut: {msg_type}")

    # ======== Cicle Percepcio-Decisio-Accio ========

    def perceive(self) -> Dict[str, Any]:
        """
        Percepcio: obté la posicio actual i estat de l'exploracio.
        """
        try:
            pos = self.mc.player.getTilePos()
            
            return {
                "position": (pos.x, pos.y, pos.z),
                "temporal_coords": self.temporal_coords,
                "temporal_range": self.temporal_range,
                "failed_searches": self.failed_searches,
                "exploration_complete": self.exploration_complete
            }
        except Exception as e:
            self.log.error(f"Error en percepcio: {e}")
            return {}

    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decisio: decideix si explorar o esperar.
        """
        # Si ja hem explorat, idle
        if perception.get("exploration_complete", False):
            return {"action": "idle"}

        # Si hem fallat massa vegades, error
        if perception.get("failed_searches", 0) >= self.MAX_SEARCH_ATTEMPTS:
            return {"action": "error", "reason": "Massa intents fallits"}

        # Decidir explorar
        origin = perception.get("temporal_coords") or perception.get("position")
        
        return {
            "action": "explore",
            "origin": origin
        }

    def act(self, action: Dict[str, Any]) -> None:
        """
        Accio: executa l'exploracio del terreny.
        """
        action_type = action.get("action")

        if action_type == "explore":
            origin = action.get("origin")
            if origin:
                self.log.info(f"Explorant des de {origin}...")
                
                try:
                    # Analitzar terreny
                    map_data = self.analyze_terrain(origin)
                    self.current_map_data = map_data
                    
                    # Marcar com completat
                    self.exploration_complete = True
                    self.failed_searches = 0
                    
                    # Enviar dades al Builder
                    self._send_map_to_builder(map_data)
                    
                    self.mc.postToChat(f"[Explorer] Exploracio completada!")
                    self.mc.postToChat(f"  Regions planes: {len(map_data.flat_region)}")
                    self.mc.postToChat(f"  Obstacles: {len(map_data.obstacles)}")
                    self.log.info(f"Mapa generat: {map_data}")
                    
                    # Tornar a IDLE
                    self.state_manager.transition(MessageStatus.IDLE, "Exploracio completada")

                    # Si hi ha una peticio encuada, iniciar-la
                    if self.pending_request:
                        payload = self.pending_request
                        self.pending_request = None
                        self._apply_start_payload(payload)
                        self.state_manager.transition(MessageStatus.RUNNING, "Processant peticio encuada")
                        self.mc.postToChat("[Explorer] Processant peticio encuada...")
                    
                except Exception as e:
                    self.log.error(f"Error explorant: {e}")
                    self.failed_searches += 1
                    self.state_manager.transition(MessageStatus.ERROR, f"Error: {e}")
                    
        elif action_type == "error":
            reason = action.get("reason", "Error desconegut")
            self.log.error(f"Error: {reason}")
            self.state_manager.transition(MessageStatus.ERROR, reason)
            self.mc.postToChat(f"[Explorer] Error: {reason}")

        elif action_type == "idle":
            # No fer res
            pass

    # ======== Mètode d'anàlisi de terreny ========

    def _send_map_to_builder(self, map_data: MapData) -> None:
        """
        Envia les dades del terreny al Builder.
        
        Args:
            map_data: Dades del mapa explorat
        """
        try:
            # Obtenir el coordinator des del registre global (hack temporal)
            # En produccio, injectar-lo al constructor
            from ..application.coordinator import Coordinator
            
            # Crear missatge amb les dades del mapa
            # El coordinator encolarà el missatge de manera síncrona
            if hasattr(self, '_coordinator_ref'):
                self._coordinator_ref.send_control(
                    "builder",
                    MessageType.SEND_TERRAIN_DATA_MAP.value,
                    map_data.to_dict()
                )
                self.log.info("Dades enviades al Builder")
            else:
                self.log.warning("No es pot enviar dades al Builder: coordinator no disponible")
                
        except Exception as e:
            self.log.error(f"Error enviant dades al Builder: {e}")

    def analyze_terrain(self, origin) -> MapData:
        """
        Analitza el terreny al voltant de l'origen.
        
        Args:
            origin: Tupla (x, y, z) d'origen
            
        Returns:
            MapData amb informacio del terreny
        """
        elevation_map = {}
        flat_region = []
        obstacles = []

        # Coordenades d'origen
        ox, oy, oz = origin

        # Exploracio en un radi predefinit o temporal
        search_range = self.temporal_range if self.temporal_range is not None else self.default_range

        for dx in range(-search_range, search_range + 1):
            for dz in range(-search_range, search_range + 1):
                x = ox + dx
                z = oz + dz
                y = self.mc.getHeight(x, z)
                
                elevation_map[(x, z)] = y
                
                # Regio plana simple: mateixa altura que origen
                if y == oy:
                    flat_region.append((x, y, z))
                else:
                    obstacles.append((x, y, z))
        
        # Netejar temporals
        self.temporal_coords = None
        self.temporal_range = None
    
        return MapData(
            origin=(ox, oy, oz),
            elevation_map=elevation_map,
            flat_region=flat_region,
            obstacles=obstacles
        )

    # ======== Hooks opcionals ========

    def set_coordinator(self, coordinator):
        """Assigna referència al coordinator per enviar missatges."""
        self._coordinator_ref = coordinator

    def on_start(self) -> None:
        self.exploration_complete = False
        self.failed_searches = 0

    def on_stop(self) -> None:
        pass

    # ======== Helpers interns ========

    def _apply_start_payload(self, payload: Dict[str, Any]) -> None:
        """Aplica coordenades/rang des d'una peticio START i prepara estat."""
        if "x" in payload and "z" in payload:
            x = int(payload["x"])
            z = int(payload["z"])
            y = self.mc.getHeight(x, z)
            self.temporal_coords = (x, y, z)
            self.log.info(f"Coordenades especificades: {self.temporal_coords}")

        if "range" in payload:
            self.temporal_range = int(payload["range"])
            self.log.info(f"Rang especificat: {self.temporal_range}")

        # Reset d'estat d'exploracio
        self.exploration_complete = False
        self.failed_searches = 0
