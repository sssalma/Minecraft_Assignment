import time
from .mining_interface import MiningStrategy

class VeinMining(MiningStrategy):
    """
    Per simular l'excavació VeinMining (trencar blocs conectats)"""

    def mine(self, miner, material: str, amount: int) -> int:
        miner.mc.post_chat(
            f"Miner: mineria per vetes de {amount} {material}"
        )

       #per testeig
        time.sleep(2)

        available = miner.inventory.available(material)

        if available <= 0:
            return 0

        # Simulem millor rendiment (fins a +20%)
        bonus = int(amount * 0.2)
        effective_amount = amount + bonus

        return min(available, effective_amount)
