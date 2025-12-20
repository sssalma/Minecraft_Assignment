import time


class ChatListener:
    """
    Adaptador: Comandes de chat Minecraft -> control de sistema.
    Es fa passant pel coordinador, no té accés al bus.
    """


    def __init__(self, mc_client, coordinator):
        self.mc = mc_client
        self.coordinator= coordinator

    def listen(self):
        try:
            chat_events = self.mc.poll_chat()
        except ValueError as e:
        # Error conegut de mcpi amb certs missatges
            print("[ChatListener] Error llegint el xat:", e)
            return
        for event in chat_events:
            message = event.message.strip().lower() #es normalitza 
            self.handle_command(message)            #es processar

    def handle_command(self, message: str):
        """
        Traducció pel coordinador.
        """
        if message == "pause":
            self.coordinator.send_control("ALL", "pause")

        elif message == "resume":
            self.coordinator.send_control("ALL", "resume")

        elif message == "stop":
            self.coordinator.send_control("ALL", "stop")

        elif message == "explorer start":
            self.coordinator.send_control("ExplorerBot", "start")
