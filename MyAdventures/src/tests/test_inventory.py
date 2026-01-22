from src.domain.inventory import Inventory

def test_inventory_add():
    inv = Inventory()
    inv.add("stone", 3)
    assert inv.available("stone") == 3

