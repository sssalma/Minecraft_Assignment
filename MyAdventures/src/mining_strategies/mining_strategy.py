"""Interfície d'estratègia de mineria."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..agents.miner import MinerAgent


class MiningStrategy(ABC):
    """
    Classe base per estratègies de mineria.
    Cada estratègia defineix com minar materials del món.
    """

    @abstractmethod
    def mine(self, miner, material, amount):
        """
        Executa operació de mineria.
        
        Args:
            miner: Instància de MinerAgent (té mc, inventory, coords)
            material: Material objectiu a prioritzar (però mina qualsevol trobat)
            amount: Nombre objectiu de blocs a minar en total
            
        Returns:
            Dict de {nom_material: comptador} de tots els blocs minats i afegits a l'inventari
        """
        pass

    @abstractmethod
    def get_name(self):
        """Retorna el nom de l'estratègia per mostrar."""
        pass
