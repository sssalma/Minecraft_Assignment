"""ChatListener - Adapter pattern for Minecraft chat commands."""
from ..messaging.enums.message_types import MessageType


class ChatListener:
    """
    Adaptador: Comandes de chat Minecraft -> missatges del sistema.
    Tradueix comandes de text a missatges estructurats pel Coordinator.
    """

    def __init__(self, mc_client, coordinator):
        """
        Inicialitza el ChatListener.
        
        Args:
            mc_client: Client de Minecraft (mcpi)
            coordinator: Instància del Coordinator
        """
        self.mc = mc_client
        self.coordinator = coordinator

    def listen(self):
        """
        Escolta esdeveniments de chat de Minecraft i els processa.
        Cridat repetidament des del main loop.
        """
        try:
            chat_events = self.mc.events.pollChatPosts()
        except ValueError as e:
            # Error conegut de mcpi amb certs missatges
            print(f"[ChatListener] Error llegint el xat: {e}")
            return
        except AttributeError:
            # Si no hi ha events.pollChatPosts, provar poll_chat
            try:
                chat_events = self.mc.poll_chat()
            except Exception as e:
                print(f"[ChatListener] Error llegint chat: {e}")
                return

        for event in chat_events:
            message = event.message.strip().lower()  # Normalitzar
            self.handle_command(message)

    def handle_command(self, message: str):
        """
        Processa una comanda de chat i l'envia al Coordinator.
        
        Args:
            message: Text de la comanda (ja normalitzat)
        """
        command = message.split()
        if not command:
            return

        # Switch/case amb match per interpretar comandes
        match command:
            # ======== Comandes globals (tots els agents) ========
            case ["agent", "stop"]:
                self.coordinator.send_control("ALL", MessageType.STOP_AGENT.value)
            case ["agent", "pause"]:
                self.coordinator.send_control("ALL", MessageType.PAUSE_AGENT.value)
            case ["agent", "resume"]:
                self.coordinator.send_control("ALL", MessageType.RESUME_AGENT.value)
            case ["agent", "status"]:
                self.coordinator.send_control("ALL", MessageType.SHOW_STATUS.value)
            case ["agent", "help"]:
                self.mc.postToChat("Comandes: agent <status|stop|pause|resume>")

            # ======== EXPLORER ========
            case ["explorer", "start", *raw_params]:
                # Formats:
                #   explorer start
                #   explorer start mode=interrupt
                #   explorer start x=10 z=20 range=15 mode=queue
                params: dict[str, object] = {}
                for raw in raw_params:
                    if "=" not in raw:
                        continue
                    key, value = raw.split("=", 1)
                    match key:
                        case "x" | "z" | "range":
                            try:
                                params[key] = int(value)
                            except ValueError:
                                continue
                        case "mode":
                            # mode=interrupt | mode=queue (queue per defecte si manca)
                            if value in {"interrupt", "queue"}:
                                params["mode"] = value

                self.coordinator.send_control("explorer", MessageType.START_MAIN_ACTION.value, params if params else None)

            case ["explorer", "stop"]:
                self.coordinator.send_control("explorer", MessageType.STOP_AGENT.value)
            case ["explorer", "pause"]:
                self.coordinator.send_control("explorer", MessageType.PAUSE_AGENT.value)
            case ["explorer", "resume"]:
                self.coordinator.send_control("explorer", MessageType.RESUME_AGENT.value)
            case ["explorer", "status"]:
                self.coordinator.send_control("explorer", MessageType.SHOW_STATUS.value)

            case ["explorer", "set", "range", range_value]:
                params = {"range": int(range_value)}
                self.coordinator.send_control("explorer", MessageType.EXPLORER_NEW_RANGE.value, params)

            # ======== MINER ========
            case ["miner", "start", position_x, position_z, position_y]:
                # Format: miner start x=10 z=20 y=64
                param_x = position_x.split("=")
                param_z = position_z.split("=")
                param_y = position_y.split("=")
                if len(param_x) == 2 and len(param_z) == 2 and len(param_y) == 2:
                    params = {
                        "x": int(param_x[1]),
                        "z": int(param_z[1]),
                        "y": int(param_y[1])
                    }
                    self.coordinator.send_control("miner", MessageType.START_MAIN_ACTION.value, params)

            case ["miner", "start", position_x, position_z]:
                param_x = position_x.split("=")
                param_z = position_z.split("=")
                if len(param_x) == 2 and len(param_z) == 2:
                    params = {"x": int(param_x[1]), "z": int(param_z[1])}
                    self.coordinator.send_control("miner", MessageType.START_MAIN_ACTION.value, params)

            case ["miner", "start"]:
                self.coordinator.send_control("miner", MessageType.START_MAIN_ACTION.value)

            case ["miner", "fulfill"]:
                self.coordinator.send_control("miner", MessageType.FULFILL_INVENTORY.value)

            case ["miner", "set", "strategy", strategy]:
                params = {"strategy": strategy}
                self.coordinator.send_control("miner", MessageType.MINER_NEW_STRATEGY.value, params)

            case ["miner", "stop"]:
                self.coordinator.send_control("miner", MessageType.STOP_AGENT.value)
            case ["miner", "pause"]:
                self.coordinator.send_control("miner", MessageType.PAUSE_AGENT.value)
            case ["miner", "resume"]:
                self.coordinator.send_control("miner", MessageType.RESUME_AGENT.value)
            case ["miner", "status"]:
                self.coordinator.send_control("miner", MessageType.SHOW_STATUS.value)
            case ["miner", "strategies"]:
                self.coordinator.send_control("miner", MessageType.SHOW_MINER_STRATEGIES.value)

            # ======== BUILDER ========
            case ["builder", "plan", "set", template]:
                params = {"template": template}
                self.coordinator.send_control("builder", MessageType.BUILDER_NEW_PLAN.value, params)

            case ["builder", "list"]:
                self.coordinator.send_control("builder", MessageType.SHOW_BUILDER_PLANS.value)

            case ["builder", "bom"]:
                # BOM = Bill of Materials (llista de materials necessaris)
                self.coordinator.send_control("builder", MessageType.BUILDER_SEND_BOM.value)

            case ["builder", "build"]:
                self.coordinator.send_control("builder", MessageType.START_MAIN_ACTION.value)

            case ["builder", "stop"]:
                self.coordinator.send_control("builder", MessageType.STOP_AGENT.value)
            case ["builder", "pause"]:
                self.coordinator.send_control("builder", MessageType.PAUSE_AGENT.value)
            case ["builder", "resume"]:
                self.coordinator.send_control("builder", MessageType.RESUME_AGENT.value)
            case ["builder", "status"]:
                self.coordinator.send_control("builder", MessageType.SHOW_STATUS.value)

            # ======== Comanda desconeguda ========
            case _:
                self.mc.postToChat(f"[!] Comanda desconeguda: {' '.join(command)}")
                self.mc.postToChat("Prova: agent help | miner/builder/explorer <action>")
