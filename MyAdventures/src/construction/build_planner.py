class BuildPlanner:
    """
    Converteix MapData + BOM en un pla de construccio simple.
    """

    def __init__(self, map_data, bom):
        self.map_data = map_data
        self.bom = bom


    #1. origen de construccio
    def select_build_origin(self):
        ox, oy, oz = self.map_data.origin
        if (ox, oy, oz) in self.map_data.flat_region:
            return (ox, oy, oz)
        return self.map_data.flat_region[0]


    #2: generar el pla
    def create_plan(self):
        """
        Genera un BuildPlan a partir del BOM.
        """
        origin = self.select_build_origin()
        ox, oy, oz = origin

        plan = []
        current_y = oy

        for phase in self.bom.phases:

            blocks = self._generate_blocks(ox, current_y, oz, phase.amount)
            
            plan.append({
                "phase": phase.name,
                "material": phase.material,
                "blocks": blocks
            })
            current_y+=1

        return plan

    # 3: geometria simple
    def _generate_blocks(self, ox, y, oz, amount):
        blocks = []
        for i in range(amount):
            blocks.append((ox + i, y, oz))

        return blocks
