import time
from .mining_interface import MiningStrategy

class VerticalMining(MiningStrategy):
    """
    Per simular l'excavació cap avall.
    """
    def mine(self, miner, material: str, amount: int) -> int:

        #retorna el que s'extreu i el miner és el que modifica l'inventari. 
        miner.mc.post_chat(
            f"Miner: mineria vertical de {amount} {material}"
        )

        # Simulació de temps de mineria
        time.sleep(1)

        # Quantitat disponible real
        available = miner.inventory.available(material)

        # Quantitat que realment es pot subministrar
        extracted = min(available, amount)

        return extracted
