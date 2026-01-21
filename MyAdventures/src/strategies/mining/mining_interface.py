from abc import ABC, abstractmethod

class MiningStrategy(ABC):
    """
    Contracte per a estratègies de mineria.
    Patró: Strategy.
    """

    @abstractmethod
    def mine(self, miner,amount: int) -> dict:
        """
        Executa l'estratègia de mineria.

        :param miner: instància del MinerBot (context)
        :param material: material a extreure
        :param amount: quantitat sol·licitada
        :return: quantitat realment extreta
        """
        pass
