catalog = [
    {"name": "Кроссовки", "price": 8500, "qty": 3},
    {"name": "Ботинки", "price": 15000, "qty": 1},
    {"name": "Туфли", "price": 12000, "qty": 5},
    {"name": "Сандалии", "price": 4500, "qty": 8},
    {"name": "Кеды", "price": 6000, "qty": 2}
]


def sort_key(item):
    return 0 if item["qty"] > 5 else 1

sorted_catalog = sorted(catalog, key=sort_key)

print("Каталог с индикатором:")
for index, item in enumerate(sorted_catalog, start=1):
    indicator = "много" if item["qty"] > 5 else "мало"

    print(f"{index}. {item['name'].ljust(12)} — {item['qty']} шт. → {indicator}")