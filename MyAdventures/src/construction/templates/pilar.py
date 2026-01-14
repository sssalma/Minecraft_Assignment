"""Pillar construction template."""
from .template_base import BuildTemplate
from ...domain.bom import BOM, BOMPhase
from ...domain.map_data import MapData


class Pilar(BuildTemplate):
    """A tall decorative pillar."""

    def __init__(self):
        super().__init__(
            name="pilar",
            description="A tall stone pillar with decorative top"
        )

    def generate_bom(self, map_data: MapData) -> BOM:
        """Generate BOM for a pillar."""
        phases = [
            BOMPhase(name="base", material="stone", amount=4),
            BOMPhase(name="column", material="stone", amount=20),
            BOMPhase(name="top", material="stone", amount=9),
        ]
        return BOM(phases)

    def get_build_positions(self, origin: tuple) -> dict:
        """
        Return dict of phase -> list of (x, y, z, material) positions.
        2x2 pillar, 10 blocks tall.
        """
        ox, oy, oz = origin

        return {
            "base": [
                (ox, oy, oz, "stone"),
                (ox + 1, oy, oz, "stone"),
                (ox, oy, oz + 1, "stone"),
                (ox + 1, oy, oz + 1, "stone"),
            ],
            "column": [
                (ox + dx, oy + h, oz + dz, "stone")
                for h in range(1, 11)
                for dx in range(2)
                for dz in range(2)
            ],
            "top": [
                (ox + i, oy + 11, oz + j, "stone")
                for i in range(3)
                for j in range(3)
            ],
        }
