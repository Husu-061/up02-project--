catalog = [
    {"name": "Кроссовки", "price": 8500, "qty": 3},
    {"name": "Ботинки", "price": 15000, "qty": 1},
    {"name": "Туфли", "price": 12000, "qty": 5},
    {"name": "Сандалии", "price": 4500, "qty": 8},
    {"name": "Кеды", "price": 6000, "qty": 2}
]

total_sum = 0

print("Каталог товаров:")
for index, item in enumerate(catalog, start=1):
    line_total = item["price"] * item["qty"]
    total_sum += line_total

    print(f"{index}. {item['name'].ljust(12)} — {item['price']} × {item['qty']} = {line_total} руб.")

print("-" * 30)
print(f"Итого: {total_sum} руб.")
