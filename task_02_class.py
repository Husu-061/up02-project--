class Product:
    def __init__(self, name, price, qty):
        self.name = name
        self.price = price
        self.qty = qty

    def total(self):
        return self.price * self.qty

    def info(self):
        return f"{self.name}: {self.price} × {self.qty} = {self.total()} руб."


item1 = Product("Кроссовки", 8500, 3)
item2 = Product("Ботинки", 15000, 1)
item3 = Product("Туфли", 12000, 5)

print(item1.info())
print(item2.info())
print(item3.info())
