class BOMPhase:

    #es com un iterador de fases
    def __init__(self, name, material, amount):
        self.name = name
        self.material = material
        self.amount = amount


class BOM:
    def __init__(self, phases):
        self.phases = phases
        self.current_phase_index = 0

    def has_next_phase(self):
        return self.current_phase_index < len(self.phases)

    def current_phase(self):
        if not self.has_next_phase():
            return None
        return self.phases[self.current_phase_index]

    def advance(self):
        self.current_phase_index += 1
