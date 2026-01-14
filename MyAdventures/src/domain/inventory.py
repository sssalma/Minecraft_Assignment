class Inventory:
    def __init__(self):
        self.stock = {}

    def add(self, material, amount):
        self.stock[material] = self.stock.get(material, 0) + amount

    def has(self, material, amount):
        return self.stock.get(material, 0) >= amount

    def consume(self, material, amount):
        if not self.has(material, amount):
            return False
        self.stock[material] -= amount
        return True

    def available(self, material):
        return self.stock.get(material, 0)
