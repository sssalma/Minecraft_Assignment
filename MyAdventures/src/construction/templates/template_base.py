from abc import ABC, abstractmethod
from domain.bom import BOM
from domain.map_data import MapData

class BuildTemplate(ABC):
    """
    Base class for construction templates.
    Each template defines what structure to build and the materials needed.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    @abstractmethod
    def generate_bom(self, map_data: MapData) -> BOM:
        """Generate BOM (Bill of Materials) for this template."""
        pass
    
    @abstractmethod
    def get_build_positions(self, origin: tuple) -> dict:
        """
        Return dict of phase -> list of (x, y, z, block_type) positions.
        
        Example:
        {
            "legs": [(x1, y1, z1, "stone"), (x2, y2, z2, "stone")],
            "surface": [(x3, y3, z3, "wood"), ...]
        }
        """
        pass
