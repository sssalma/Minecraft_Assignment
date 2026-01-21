import time
import mcpi.block as block
from .mining_interface import MiningStrategy


class GridMining(MiningStrategy):

    def block_to_material(self, block_id: int) -> str:
        if block_id == 1:
            return "stone"
        if block_id == 17:
            return "wood"
        if block_id in (2, 3):
            return "dirt"
        return "other"

    def mine(self, miner, amount):
        mc = miner.mc.get_mc()
        pos = mc.player.getTilePos()

        mined = {}
        mined_count = 0

        miner.mc.post_chat("Miner: mineria en graella REAL")

        # graella 5x5 a nivell del jugador
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if mined_count >= amount:
                    return mined

                x = pos.x + dx
                y = pos.y
                z = pos.z + dz

                block_id = mc.getBlock(x, y, z)
                if block_id in (0, 7, 8, 9, 10, 11):
                    continue

                mc.setBlock(x, y, z, block.AIR.id)

                material = self.block_to_material(block_id)
                mined[material] = mined.get(material, 0) + 1
                mined_count += 1

                time.sleep(0.1)

        return mined
