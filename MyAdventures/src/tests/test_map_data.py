from src.domain.map_data import MapData

def test_mapdata_valid():
    md = MapData(
        origin=(0, 0, 0),
        elevation_map={(0,0):0},
        flat_region=[(0,0,0)],
        obstacles=[]
    )
    assert md.is_valid()


