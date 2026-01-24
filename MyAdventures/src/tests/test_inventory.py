from src.domain.inventory import Inventory

def test_inventory_add():
    inv = Inventory()
    inv.add("stone", 3)
    assert inv.available("stone") == 3

def test_inventory_has_and_consume():
    inv = Inventory()
    inv.add("iron", 5)

    assert inv.has("iron", 3) is True
    assert inv.consume("iron", 3) is True
    assert inv.available("iron") == 2


def test_inventory_consume_not_enough_material():
    inv = Inventory()
    inv.add("wood", 1)

    assert inv.consume("wood", 5) is False
    assert inv.available("wood") == 1
