from .agent_base import BaseAgent

class BuilderBot(BaseAgent):  ################builder de prova
    def __init__(self, mc):
        super().__init__("BuilderBot", mc)

    def perceive(self): 
        return None

    def decide(self, perception):
        return "wait"

    def act(self, action):
        pass

    def process_message(self, msg):
        # crido al process_message del pare pk l'estic sobreescribint
        super().process_message(msg)

        # comprovo si el missatge és el mapa de l'explorer 
        if msg.msg_type == "map.v1":
            print(f"[{self.name}] !!! HE REBUT DADES DE {msg.source} !!!")
            print(f"[{self.name}] Payload: {msg.payload}")
            
            # missatge al joc
            self.mc.postToChat("Builder: Connexio confirmada! He rebut el mapa.")