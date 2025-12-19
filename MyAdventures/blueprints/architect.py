class Architect:
    def __init__(self):
        # Aquí podrías cargar un JSON externo (templates.json)
        # De momento lo dejamos aquí para que sea fácil de probar
        self.templates = {
            "basic_house": [
                {"phase": "Foundation", "material": "STONE", "id": 1, "shape": "3x3_base"},
                {"phase": "Pilar", "material": "WOOD", "id": 17, "shape": "center_column_2"},
                {"phase": "Roof", "material": "GOLD", "id": 41, "shape": "top_cap"}
            ]
        }
        self.current_plan = None
        self.origin = None

    def load_plan(self, template_name, origin_coords):
        """Carga un plano y establece el punto de origen"""
        if template_name in self.templates:
            self.current_plan = self.templates[template_name]
            self.origin = origin_coords
            return True
        return False

    def get_total_phases(self):
        return len(self.current_plan) if self.current_plan else 0

    def get_phase_requirements(self, phase_index):
        """Devuelve qué material y cuánto se necesita para esta fase"""
        if not self.current_plan: return None
        
        phase_data = self.current_plan[phase_index]
        shape_type = phase_data["shape"]
        
        # Calculamos la cantidad segun la forma (Lógica encapsulada)
        count = 0
        if shape_type == "3x3_base": count = 9
        elif shape_type == "center_column_2": count = 2
        elif shape_type == "top_cap": count = 1
        
        return {
            "material": phase_data["material"],
            "count": count,
            "phase_name": phase_data["phase"]
        }

    def generate_build_queue(self, phase_index):
        """Devuelve la lista EXACTA de coordenadas (x,y,z,id) para construir"""
        if not self.origin: return []
        
        phase_data = self.current_plan[phase_index]
        shape = phase_data["shape"]
        block_id = phase_data["id"]
        
        cx, cy, cz = self.origin["x"], self.origin["y"], self.origin["z"]
        queue = []

        # Toda la matemática "sucia" está escondida aquí
        if shape == "3x3_base":
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    queue.append((cx + dx, cy, cz + dz, block_id))
                    
        elif shape == "center_column_2":
            queue.append((cx, cy + 1, cz, block_id))
            queue.append((cx, cy + 2, cz, block_id))
            
        elif shape == "top_cap":
            queue.append((cx, cy + 3, cz, block_id))
            
        return queue