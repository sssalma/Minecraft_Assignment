from src.domain.bom import BOM, BOMPhase

def test_bom_advance():
    bom = BOM([
        BOMPhase("phase1", "stone", 2),
        BOMPhase("phase2", "wood", 1)
    ])

    assert bom.current_phase().name == "phase1"
    bom.advance()
    assert bom.current_phase().name == "phase2"

