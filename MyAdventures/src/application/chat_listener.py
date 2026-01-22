import time
import src.runtime.workflow_manager as workflow_manager

class ChatListener:
    """
    Adaptador: Comandes de chat Minecraft -> control de sistema.
    Es fa passant pel coordinador, no té accés al bus.
    """


    def __init__(self, mc_client, workflow_manager):
        self.mc = mc_client
        self.workflow_manager = workflow_manager

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
        
        if message == "explorer start":
            wf_id = self.workflow_manager.start_workflow()
            print(f"Workflow {wf_id} iniciat.")

        elif message == "agent help":
            self.mc.postToChat("Decisió de disseny: Les comandes s'apliquen a l'ultim workflow creat.")
            self.mc.postToChat("Comandes disponibles:")
            self.mc.postToChat("agent help   - mostra aquesta ajuda")
            self.mc.postToChat("agent status - estat dels agents")
            self.mc.postToChat("agent pause  - pausa agents en execució")
            self.mc.postToChat("agent resume - reprèn agents pausats")
            self.mc.postToChat("agent stop   - atura el workflow")

        elif message == "agent stop":
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.postToChat("No hi ha cap workflow actiu")
                return
            self.workflow_manager.stop_workflow()
            self.mc.postToChat("Workflow aturat")

        elif message == "agent status":
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.postToChat("No hi ha cap workflow actiu")
                return

            status = wf.observer.get_status()

            if not status:
                self.mc.postToChat("Encara no hi ha informació d'estat")
                return

            # MAP: dict -> llista de strings 
            lines = map(
                    lambda item: f"{item[0]}: {item[1]}",
                    status.items() ) 
            for line in lines:
                self.mc.postToChat(line)

        elif message == "agent pause":
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.postToChat("No hi ha cap workflow actiu")
                return
            
            #uso l'observer per saber l'estat
            # i FILTRO els que estàn actius : NO idle i no stopped
            status = wf.observer.get_status()
            running_agents = filter(
                lambda item: item[1] not in ("IDLE", "STOPPED","ERROR"),
                status.items()
            )
            for agent_name, _ in running_agents:
                wf.coordinator.send_control(agent_name, "pause")
            self.mc.postToChat("Agents en execució pausats")

        elif message == "agent resume":
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.postToChat("No hi ha cap workflow actiu")
                return
            #uso l'observer per saber l'estat i FILTRO els que estàn PAUSED
            status = wf.observer.get_status()
            paused_agents = filter(
                lambda item: item[1] == "PAUSED",
                status.items()
            )
            for agent_name, _ in paused_agents:
                wf.coordinator.send_control(agent_name, "resume")
            self.mc.postToChat("Agents pausats reactivats")
        elif message == "stop":
            self.workflow_manager.stop_workflow()
            self.mc.postToChat("Workflow aturat")

        elif message.startswith("explorer start"): #explorer start + específic
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.postToChat("No hi ha cap workflow actiu")
                return

            parts = message.split()
            args = dict(
                map(
                    lambda kv: kv.split("="),
                    filter(lambda p: "=" in p, parts)
                )
            )
            wf.coordinator.send_control(
                target="ExplorerBot",
                command="start",
                payload=args
            )
            self.mc.postToChat(f"Explorer iniciat amb params {args}")
        elif message == "workflow list":
            ids = self.workflow_manager.list_workflows()
            self.mc.postToChat(f"Workflows actius: {ids}")

        elif message.startswith("miner set strategy"):
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.postToChat("No hi ha cap workflow actiu")
                return
            parts = message.split()

            if len(parts) < 4:
                self.mc.postToChat("Canviant estratègia.")
                return

            strategy = parts[-1]
            wf.coordinator.send_strategy(
                target="MinerBot",
                strategy_name=strategy
            )
            self.mc.postToChat(f"Estratègia del Miner canviada a {strategy}")