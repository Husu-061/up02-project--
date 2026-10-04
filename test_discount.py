"""Тестирование алгоритма скидки."""
from datetime import datetime
from discount import calculate_price_with_discount


def run_tests():
    """Прогон тестов."""
    date = datetime(2026, 10, 15)

    # Формат: (id, базовая цена, ожидаемая цена, пояснение)
    test_cases = [
        (1, 100, 100, "The Beatles - Hey Jude — есть заказ в сентябре"),
        (2, 120, 120, "Michael Jackson - Billie Jean — есть заказ в сентябре"),
        (3, 90, 90, "Louis Armstrong — есть заказ в сентябре"),
        (4, 150, 112.5, "Бетховен — нет заказов → скидка 25%"),
        (5, 110, 82.5, "Eminem - Lose Yourself — нет заказов → скидка 25%"),
        (6, 130, 97.5, "Daft Punk - Get Lucky — нет заказов → скидка 25%"),
        (7, 100, 75.0, "Би-2 — нет заказов → скидка 25%"),
    ]

    print("=" * 60)
    print("ТЕСТИРОВАНИЕ АЛГОРИТМА СКИДКИ (МУЗЫКАЛЬНЫЙ МАГАЗИН)")
    print("=" * 60)

    passed = 0
    for product_id, price, expected, comment in test_cases:
        result = calculate_price_with_discount(product_id, price, date)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} Товар {product_id}: {price} → {result} "
              f"(ожидалось {expected}) — {comment}")

    print("=" * 60)
    print(f"Пройдено: {passed} / {len(test_cases)}")


if __name__ == "__main__":
    run_tests()