import time
import mcpi.block as block
from .mining_interface import MiningStrategy


class VeinMining(MiningStrategy):

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

        miner.mc.post_chat("Miner: mineria per vetes REAL")

        # centre + veïns (cross)
        positions = [
            (pos.x, pos.y - 1, pos.z),
            (pos.x + 1, pos.y - 1, pos.z),
            (pos.x - 1, pos.y - 1, pos.z),
            (pos.x, pos.y - 1, pos.z + 1),
            (pos.x, pos.y - 1, pos.z - 1),
        ]

        for x, y, z in positions:
            if mined_count >= amount:
                break

            block_id = mc.getBlock(x, y, z)
            if block_id in (0, 7, 8, 9, 10, 11):
                continue

            mc.setBlock(x, y, z, block.AIR.id)

            material = self.block_to_material(block_id)
            mined[material] = mined.get(material, 0) + 1
            mined_count += 1

            time.sleep(0.15)

        return mined
