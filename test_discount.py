"""Тестирование алгоритма скидки."""
from datetime import datetime
from discount import calculate_price_with_discount


def run_tests():
    """Прогон тестов."""
    
    # Создаем разные даты для тестов
    date1 = datetime(2026, 10, 15)
    date2 = datetime(2026, 11, 15)
    date3 = datetime(2026, 12, 1)
    date4 = datetime(2026, 10, 20)
    date5 = datetime(2026, 11, 10)

    # (id, цена, ожидание, пояснение, дата)
    test_cases = [
        # Старые 5 тестов (оставляем для истории)
        (1, 100, 100, "The Beatles — остаток > 3", date1),
        (2, 120, 120, "Michael Jackson — остаток > 3", date1),
        (3, 90, 90, "Louis Armstrong — остаток > 3", date1),
        (4, 150, 150, "Бетховен — остаток > 3", date1),
        (5, 110, 110, "Eminem — остаток > 3", date1),
        
        # 👇 ВАШИ 5 НОВЫХ ТЕСТОВ 👇
        (6, 130, 130, "Daft Punk — остаток > 3", date2),
        (7, 100, 100, "Би-2 — остаток > 3", date3),
        (1, 100, 100, "The Beatles — другая дата", date4),
        (4, 150, 150, "Бетховен — другая дата", date5),
        (2, 120, 120, "Michael Jackson — другая дата", date3),
        
                # 👇 5 НОВЫХ ТЕСТОВ С УЧЕТОМ ИЗМЕНЕНИЙ В БД (остаток 2) 👇
        (6, 130, 117.0, "Daft Punk — остаток 2 → скидка 10%", date2),
        (7, 100, 90.0, "Би-2 — остаток 2 → скидка 10%", date3),
        (1, 100, 100, "The Beatles — остаток 50", date4),
        (4, 150, 135.0, "Бетховен — остаток 2 → скидка 10%", date5),
        (2, 120, 120, "Michael Jackson — остаток 40", date3),
    ]

    print("=" * 60)
    print("ТЕСТИРОВАНИЕ АЛГОРИТМА СКИДКИ (ОСТАТОК <= 3)")
    print("=" * 60)

    passed = 0
    for product_id, price, expected, comment, test_date in test_cases:
        result = calculate_price_with_discount(product_id, price, test_date)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} Товар {product_id}: {price} → {result} "
              f"(ожидалось {expected}) — {comment}")

    print("=" * 60)
    print(f"Пройдено: {passed} / {len(test_cases)}")


if __name__ == "__main__":
    run_tests()