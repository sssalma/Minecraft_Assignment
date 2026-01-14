"""Registre d'estratègies de mineria."""
from .vertical_mining import VerticalMining
from .grid_mining import GridMining

# Taula d'estratègies disponibles
_STRATEGIES = dict()
_STRATEGIES["vertical"] = VerticalMining
_STRATEGIES["grid"] = GridMining


def list_strategies():
    """Retorna llista de noms d'estratègies disponibles."""
    # Extreure claus del diccionari
    keys = list(_STRATEGIES.keys())
    return keys


def get_strategy(name):
    """
    Obté una instància d'estratègia per nom.
    
    Args:
        name: Nom de l'estratègia (ex: "vertical", "grid")
        
    Returns:
        Instància d'estratègia o None si no es troba
    """
    # Normalitzar nom a minúscules
    name_lower = name.lower()
    
    # Buscar classe d'estratègia al registre
    strategy_class = None
    
    for key in _STRATEGIES.keys():
        if key == name_lower:
            strategy_class = _STRATEGIES[key]
            break
    
    # Instanciar estratègia si es troba
    if strategy_class is not None:
        instance = strategy_class()
        return instance
    
    return None
