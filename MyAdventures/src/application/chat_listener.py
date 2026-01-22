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
            self.mc.post_chat("Decisió de disseny: Les comandes s'apliquen a l'ultim workflow creat.")
            self.mc.post_chat("Comandes disponibles:")
            self.mc.post_chat("agent help   - mostra aquesta ajuda")
            self.mc.post_chat("agent status - estat dels agents")
            self.mc.post_chat("agent pause  - pausa agents en execució")
            self.mc.post_chat("agent resume - reprèn agents pausats")
            self.mc.post_chat("agent stop   - atura el workflow")

        elif message == "agent stop":
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.post_chat("No hi ha cap workflow actiu")
                return
            self.workflow_manager.stop_workflow()
            self.mc.post_chat("Workflow aturat")

        elif message == "agent status":
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.post_chat("No hi ha cap workflow actiu")
                return

            status = wf.observer.get_status()

            if not status:
                self.mc.post_chat("Encara no hi ha informació d'estat")
                return

            # MAP: dict -> llista de strings 
            lines = map(
                    lambda item: f"{item[0]}: {item[1]}",
                    status.items() ) 
            for line in lines:
                self.mc.post_chat(line)

        elif message == "agent pause":
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.post_chat("No hi ha cap workflow actiu")
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
            self.mc.post_chat("Agents en execució pausats")

        elif message == "agent resume":
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.post_chat("No hi ha cap workflow actiu")
                return
            #uso l'observer per saber l'estat i FILTRO els que estàn PAUSED
            status = wf.observer.get_status()
            paused_agents = filter(
                lambda item: item[1] == "PAUSED",
                status.items()
            )
            for agent_name, _ in paused_agents:
                wf.coordinator.send_control(agent_name, "resume")
            self.mc.post_chat("Agents pausats reactivats")
        elif message == "stop":
            self.workflow_manager.stop_workflow()
            self.mc.post_chat("Workflow aturat")

        elif message.startswith("miner set strategy"):
            wf = self.workflow_manager.get_workflow()
            if not wf:
                self.mc.post_chat("No hi ha cap workflow actiu")
                return
            parts = message.split()

            if len(parts) < 4:
                self.mc.post_chat("Canviant estratègia.")
                return

            strategy = parts[-1]
            wf.coordinator.send_strategy(
                target="MinerBot",
                strategy_name=strategy
            )
            self.mc.post_chat(f"Estratègia del Miner canviada a {strategy}")