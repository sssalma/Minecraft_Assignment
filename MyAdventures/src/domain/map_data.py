class MapData:
    """
    Structured representation of terrain analysis results.
    """

    def __init__(self, origin, elevation_map, flat_region, obstacles):
        self.origin = origin              # (x, y, z)
        self.elevation_map = elevation_map  # dict {(x,z): y}
        self.flat_region = flat_region     # list[(x,y,z)]
        self.obstacles = obstacles         # list[(x,y,z)]

    def is_valid(self):
        """
        A map is valid if a flat region exists.
        """
        return self.flat_region is not None and len(self.flat_region) > 0

    def to_payload(self):
        """
        Serializes MapData to a JSON-compatible payload.
        """
        return {
            "origin": self.origin,
            "elevation_map": self.elevation_map,
            "flat_region": self.flat_region,
            "obstacles": self.obstacles
        }
