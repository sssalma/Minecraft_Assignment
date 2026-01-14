from mcpi.minecraft import Minecraft

class MinecraftClient:
    def __init__(self):
        self.mc = Minecraft.create()

    def post_chat(self, message: str):
        self.mc.postToChat(message)

    def poll_chat(self):
        return self.mc.events.pollChatPosts()

    def get_mc(self):
        """Acceso controlado al cliente mcpi si algún agente lo necesita"""
        return self.mc

    # --- Convenience queries for block inspection ---
    def get_block_id(self, x: int, y: int, z: int) -> int:
        """Return block id at (x,y,z)."""
        return self.mc.getBlock(x, y, z)

    def get_block_name(self, x: int, y: int, z: int) -> str | None:
        """Return symbolic block name (e.g., 'STONE') for id at (x,y,z)."""
        try:
            block_id = self.get_block_id(x, y, z)
            # Map id -> constant name via mcpi.block definitions
            from mcpi import block as mcblock
            for name, obj in mcblock.__dict__.items():
                if isinstance(obj, mcblock.Block) and obj.id == block_id:
                    return name
            return f"UNKNOWN({block_id})"
        except Exception:
            return None