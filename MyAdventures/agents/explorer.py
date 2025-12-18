from .agent_base import BaseAgent
import time

class ExplorerBot(BaseAgent):

    #crido al constructor del pare
    def __init__(self, mc): 
        super().__init__("ExplorerBot", mc)
        self.search_radius = 10
        self.last_search_time= 0

    #ubico al jugador: pos (getTilePos())+ alçada getHeight(pos.x, pos.z))
    def perceive(self):
        try:
         pos = self.mc.player.getTilePos()
         return pos
        except:
            return None
            
    #decideix si está elevat del terra
    def decide(self, perception):
        if not perception: return "wait"

        #decidir cada 2 segons per no saturar la cpu
        if time.time() - self.last_search_time <2:
            return "wait"
        self.last_search_time= time.time()

        #El default es buscar una zona de 3x3
        found_location = self.find_flat_area(perception, size = 3)

        if found_location:
            return ("found_site", found_location)
        else:
            self.mc.postToChat("Explorer: Buscant zona plana..")
            return "keep_searching"

    def act(self, action):
        
        if action == "wait":
            return
        if action == "keep_searching":
            return
        
        if not isinstance(action, str):
            action_type = action[0]
            data=action[1]

            #preparo el missatge a enviar
            if action_type == "found_site":
                location = data

                payload ={
                    "coordinates": location,
                    "structure_type": "estructura_test",
                    "required_material": "STONE"
                }
            #l'envio i notifico
            self.send_message("BuilderBot", "map.v1", payload)
            self.mc.postToChat(f"Explorer: Zona trobada a {location['x']}, {location['z']}! Dades enviades.")

            # Canvio l'estat a IDLE
            self.set_state("IDLE")

    def find_flat_area(self, center_pos, size=3):
        """
        Escaneja l'entorn per trobar una superfície plana de size x size.
        Retorna un diccionari {x, y, z} o None.
        """
        start_x = center_pos.x - self.search_radius
        end_x = center_pos.x + self.search_radius
        start_z = center_pos.z - self.search_radius
        end_z = center_pos.z + self.search_radius

        # recorro tots els punts del cuadrat en els eixos x i z
        for x in range(start_x, end_x):
            for z in range(start_z, end_z):
                #per cada punt:  comprobo l'alçada + mira si es pla
                y = self.mc.getHeight(x, z)
                
                #is_flat per veure si l'àrea del cuadrat (3*3) es plana 
                if self.is_flat(x, y, z, size):
                    return {"x": x, "y": y, "z": z}
        return None

    def is_flat(self, x, y, z, size):
        """Comprova si tots els blocs de l'àrea tenen la mateixa alçada."""
        # Un quadrat petit (size x size)
        for dx in range(size):
            for dz in range(size):
                height = self.mc.getHeight(x + dx, z + dz)
                if height != y:
                    return False
        return True