from .agent_base import BaseAgent
from blueprints.architect import Architect
import time

class BuilderBot(BaseAgent):  ###builder de prova
    def __init__(self, mc):
        super().__init__("BuilderBot", mc)
        self.architect = Architect()
        self.current_plan = None

        self.current_stage_index = 0
        self.required_amount = 0
        self.current_inventory = 0
        self.last_material_time = 0
        self.TIMEOUT_LIMIT = 20

    def perceive(self): 
        return len(self.build_queue) > 0

    def decide(self, perception):
        #evito deadlocks
        if self.state == "WAITING":
            if time.time() - self.last_material_time > self.TIMEOUT_LIMIT:
                return "timeout_error"
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
                if not self.build_queue:
                    self.mc.postToChat(f"Builder: Fase {self.current_stage_index} completada.")
                    self.advance_stage()
        if action == "timeout_error":
            self.mc.postToChat("Builder: ERROR de timeout.")
            self.set_state("ERROR")

    def on_message_received(self, msg):
        # crido al process_message del pare pk l'estic sobreescribint
        #super().process_message(msg)

        # [REBO MAPA] #CONSTRUCCIÓ  demano material i copio les coordenades
        if msg.msg_type == "map.v1":
            coords = msg.payload["coordinates"]
            print(f"[{self.name}] Mapa rebut, consultant Arquitecte...")
            
            #delego a l'arquitecte
            self.architect.load_plan("basic_house", coords)
            self.current_stage_index = -1
            self.advance_stage()

        #[REBO MATERIAL] es conta + reset timeout
        elif msg.msg_type == "material.supply":
            amount = msg.payload.get("amount")
            self.current_inventory += amount
            self.last_material_time = time.time()
            print(f"[{self.name}] Rebut: {self.current_inventory}/{self.required_amount}")

            if self.current_inventory >= self.required_amount:
                self.start_construction_phase

    def advance_stage(self):
        """Gestió de la construcció"""
        self.current_stage_index += 1
        
        # ¿Quedan fases en la plantilla?
        if self.current_stage_index < self.architect.get_total_phases():
           # què es necessita
            reqs = self.architect.get_phase_requirements(self.current_stage_index)
            
            # 1. Configurar BOM
            self.required_amount = reqs["count"]
            material_name = reqs["material"]
            phase_name = reqs["phase_name"]
            self.current_inventory = 0

            self.mc.postToChat(f"Builder: Fase {self.current_stage_index} ({phase_name}). Pidiendo {self.required_amount} de {material_name}.")
            # 2. Demanar materials
            request = {"material": material_name, "amount": self.required_amount}
            self.send_message("MinerBot", "request.material", request)
            
            # 3. Esperar
            self.last_material_time = time.time()
            self.set_state("WAITING")
            
        else:
            # ¡CASA ACABADA!
            self.mc.postToChat("Builder: PROYECTO FINALIZADO CON ÉXITO!")
            self.set_state("IDLE")

    def start_construction_phase(self):
        """Pide al arquitecto los bloques exactos y empieza a trabajar"""
        self.build_queue = self.architect.generate_build_queue(self.current_stage_index)
        
        self.mc.postToChat("Builder: Materiales listos. A trabajar.")
        self.set_state("RUNNING")