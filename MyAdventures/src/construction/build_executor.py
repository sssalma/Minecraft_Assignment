import time

class BuildExecutor:
    """
    Executa un BuildPlan al món real.
        -comprovació d'inventari

    """
    BLOCK_IDS = {
        "stone": 1,
        "wood": 5,
        "glass": 20
    }
    def __init__(self, mc, inventory):
        self.mc = mc
        self.inventory = inventory

    def execute(self, build_plan):
        for phase in build_plan:
            self._execute_phase(phase)

    def _execute_phase(self, phase):
        material = phase["material"]
        blocks = phase["blocks"]

        # comprovació d'inventari
        if self.inventory.available(material) < len(blocks):
            raise RuntimeError(
                f"No hi ha prou {material}"
            )

        self.mc.post_chat(f"Builder: construint fase {phase['phase']}")
        block_id = self.BLOCK_IDS.get(material)
        if block_id is None:
            raise ValueError(f"Material desconegut: {material}")
        for (x, y, z) in blocks:
            self.mc.get_mc().setBlock(x, y, z, block_id)
            self.inventory.consume(material, 1)
            time.sleep(0.1)
