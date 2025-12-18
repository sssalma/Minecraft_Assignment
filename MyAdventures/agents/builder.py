from .agent_base import BaseAgent
import time

class BuilderBot(BaseAgent):  ###builder de prova
    def __init__(self, mc):
        super().__init__("BuilderBot", mc)
        self.build_queue = [] 

    def perceive(self): 
        return len(self.build_queue) > 0

    def decide(self, perception):
        if perception:
            return "place_block"
        return "wait"

    def act(self, action):
        if action == "place_block":
            #Traiem el primer bloc 
            if self.build_queue:
                dades = self.build_queue.pop(0)
                x = dades[0]
                y = dades[1]
                z = dades[2]
                block_id = dades[3]

                self.mc.setBlock(x, y, z, block_id)
                time.sleep(0.05) 
            else: 
                self.mc.postToChat("Builder: Obra finalitzada.")
                self.set_state("IDLE")


    def process_message(self, msg):
        # crido al process_message del pare pk l'estic sobreescribint
        super().process_message(msg)

        # comprovo si el missatge és el mapa de l'explorer 
        if msg.msg_type == "map.v1":
            coords = msg.payload["coordinates"]
            x, y, z = coords["x"], coords["y"], coords["z"]
            print(f"[{self.name}] Construint a {x}, {y}, {z}")
            
            #ESTRUCTURA TEST (Una creu vermella començant a y+1)
            y_start = y + 1
            
            self.build_queue = []

            # la pedra tindrà una base de 3x3
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    self.build_queue.append((x + dx, y_start, z + dz, 1)) # 1 = Pedra
            
            # Un tros de color d'Or (41) al mig
            self.build_queue.append((x, y_start + 1, z, 41)) 
            self.build_queue.append((x, y_start + 2, z, 41))
            
            self.mc.postToChat(f"Builder: Construint base a {x}, {z}!")
            self.set_state("RUNNING")