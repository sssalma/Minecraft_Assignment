"""Map data structure for Explorer agent."""
from typing import Dict, List, Tuple


class MapData:
    """
    Estructura de dades per emmagatzemar informacio del terreny explorat.
    """

    def __init__(self, origin: Tuple[int, int, int],
                 elevation_map: Dict[Tuple[int, int], int],
                 flat_region: List[Tuple[int, int, int]],
                 obstacles: List[Tuple[int, int, int]]):
        """
        Inicialitza les dades del mapa.
        
        Args:
            origin: Coordenades d'origen (x, y, z)
            elevation_map: Mapa d'elevacio {(x, z): y}
            flat_region: Llista de coordenades planes [(x, y, z), ...]
            obstacles: Llista d'obstacles [(x, y, z), ...]
        """
        self.origin = origin
        self.elevation_map = elevation_map
        self.flat_region = flat_region
        self.obstacles = obstacles

    def __str__(self):
        return (f"MapData(origin={self.origin}, "
                f"flat={len(self.flat_region)}, "
                f"obstacles={len(self.obstacles)})")

    def to_dict(self):
        """Converteix a diccionari per enviar com a payload."""
        return {
            "origin": self.origin,
            "flat_region": self.flat_region,
            "obstacles": self.obstacles,
            "elevation_map": dict(self.elevation_map)
        }
