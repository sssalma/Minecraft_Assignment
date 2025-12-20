import time
from .mining_interface import MiningStrategy

class GridMining(MiningStrategy):
    """
    Per simular l'excavació en graella.
    """

    def mine(self, miner, material: str, amount: int) -> int:
        miner.mc.post_chat(
            f"Miner: mineria en graella de {amount} {material}"
        )

        time.sleep(1)

        available = miner.inventory.available(material)
        return min(available, amount)
