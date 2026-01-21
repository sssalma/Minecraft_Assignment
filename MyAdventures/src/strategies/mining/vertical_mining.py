import time
import mcpi.block as block
from .mining_interface import MiningStrategy


class VerticalMining(MiningStrategy):

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
        y = pos.y - 1

        miner.mc.post_chat("Miner: mineria vertical REAL")

        while y > 0 and sum(mined.values()) < amount:
            current = mc.getBlock(pos.x, y, pos.z)
            block_id = current.id if hasattr(current, "id") else current

            # Ignorem aire, aigua, lava, bedrock
            if block_id in (0, 7, 8, 9, 10, 11):
                y -= 1
                continue

            mc.setBlock(pos.x, y, pos.z, block.AIR.id)

            material = self.block_to_material(block_id)
            mined[material] = mined.get(material, 0) + 1

            time.sleep(0.15)
            y -= 1

        return mined
