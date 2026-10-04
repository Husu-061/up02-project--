from datetime import datetime
from models import Product

# Товар 4: Бетховен. В сентябре 2026 заказов не было -> ожидаем скидку 25%
p1 = Product(4, "Классика", "Бетховен", "Симфония №5", 500, 150, 20)

# Товар 1: The Beatles. Был заказ 15.09.2026 -> скидки не будет
p2 = Product(1, "Рок", "The Beatles", "Hey Jude", 431, 100, 50)

date = datetime(2026, 10, 15)

print("=" * 40)
print("ПРОВЕРКА АВТОМАТИЧЕСКОЙ СКИДКИ")
print("=" * 40)

print(f"\n{p1.info()}")
print(f"Базовая цена: {p1.price}")
print(f"Со скидкой: {p1.price_with_discount_auto(date)}")

print(f"\n{p2.info()}")
print(f"Базовая цена: {p2.price}")
print(f"Со скидкой: {p2.price_with_discount_auto(date)}")