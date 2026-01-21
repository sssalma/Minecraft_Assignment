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


        elif message == "stop":
            self.workflow_manager.stop_workflow()
            self.mc.post_chat("Workflow aturat")

        elif message == "workflow list":
            ids = self.workflow_manager.list_workflows()
            self.mc.post_chat(f"Workflows actius: {ids}")
