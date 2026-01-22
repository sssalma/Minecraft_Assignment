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