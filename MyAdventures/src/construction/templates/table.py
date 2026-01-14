"""Table construction template."""
from .template_base import BuildTemplate
from ...domain.bom import BOM, BOMPhase
from ...domain.map_data import MapData


class Table(BuildTemplate):
    """A simple table with legs and surface."""

    def __init__(self):
        super().__init__(
            name="table",
            description="A wooden 4x2 table with 4 legs"
        )

    def generate_bom(self, map_data: MapData) -> BOM:
        """Generate BOM for a table."""
        phases = [
            BOMPhase(name="legs", material="stone", amount=4),
            BOMPhase(name="surface", material="wood", amount=8),
        ]
        return BOM(phases)

    def get_build_positions(self, origin: tuple) -> dict:
        """
        Return dict of phase -> list of (x, y, z, material) positions.
        4x2 table at height 1, with 4 stone legs.
        """
        ox, oy, oz = origin

        return {
            "legs": [
                # 4 corner legs, 1 block tall
                (ox, oy, oz, "stone"),
                (ox + 3, oy, oz, "stone"),
                (ox, oy, oz + 1, "stone"),
                (ox + 3, oy, oz + 1, "stone"),
            ],
            "surface": [
                # 4x2 wooden surface at y+1
                (ox + i, oy + 1, oz + j, "wood")
                for i in range(4)
                for j in range(2)
            ],
        }
