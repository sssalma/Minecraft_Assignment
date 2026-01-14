"""Simple house construction template."""
from .template_base import BuildTemplate
from ...domain.bom import BOM, BOMPhase
from ...domain.map_data import MapData


class SimpleHouse(BuildTemplate):
    """A simple 5x5 house with foundation, walls, and roof."""

    def __init__(self):
        super().__init__(
            name="simple_house",
            description="A 5x5 house with stone foundation, wood walls, and glass roof"
        )

    def generate_bom(self, map_data: MapData) -> BOM:
        """Generate BOM for a simple house."""
        phases = [
            BOMPhase(name="foundation", material="stone", amount=25),
            BOMPhase(name="walls", material="wood", amount=60),
            BOMPhase(name="roof", material="wood", amount=25),
        ]
        return BOM(phases)

    def get_build_positions(self, origin: tuple) -> dict:
        """
        Return dict of phase -> list of (x, y, z, material) positions.
        Simple 5x5 house centered at origin.
        """
        ox, oy, oz = origin

        return {
            "foundation": [
                # 5x5 base
                (ox + i, oy, oz + j, "stone")
                for i in range(5)
                for j in range(5)
            ],
            "walls": [
                # 4 walls, 3 blocks high
                (ox + i, oy + 1 + h, oz, "wood")
                for i in range(5)
                for h in range(3)
            ]
            + [
                (ox + i, oy + 1 + h, oz + 4, "wood")
                for i in range(5)
                for h in range(3)
            ]
            + [
                (ox, oy + 1 + h, oz + j, "wood")
                for j in range(1, 4)
                for h in range(3)
            ]
            + [
                (ox + 4, oy + 1 + h, oz + j, "wood")
                for j in range(1, 4)
                for h in range(3)
            ],
            "roof": [
                # Simple flat roof at y+4
                (ox + i, oy + 4, oz + j, "wood")
                for i in range(5)
                for j in range(5)
            ],
        }
