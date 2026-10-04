from datetime import datetime
from discount import calculate_price_with_discount


def run_tests():
    # (product_id, price, date, expected, comment)
    test_cases = [
        # --- Базовые тесты (из ДЗ, товары с остатком > 3) ---
        (1, 100, datetime(2026, 10, 15), 100, "The Beatles — остаток > 3"),
        (2, 120, datetime(2026, 10, 15), 120, "Michael Jackson — остаток > 3"),
        (3, 90, datetime(2026, 10, 15), 90, "Louis Armstrong — остаток > 3"),
        (5, 110, datetime(2026, 10, 15), 110, "Eminem — остаток > 3"),
        
        # --- Тесты на скидку (товары с остатком <= 3) ---
        # Внимание: чтобы эти тесты прошли, в БД остаток должен быть 2!
        (4, 150, datetime(2026, 10, 15), 135.0, "Бетховен — остаток 2 → скидка 10%"),
        (6, 130, datetime(2026, 10, 15), 117.0, "Daft Punk — остаток 2 → скидка 10%"),
        (7, 100, datetime(2026, 10, 15), 90.0, "Би-2 — остаток 2 → скидка 10%"),
        
        # --- Новые тесты на разные даты ---
        (4, 150, datetime(2026, 11, 15), 135.0, "Бетховен — другая дата, остаток 2"),
        (1, 100, datetime(2026, 11, 15), 100, "The Beatles — другая дата, остаток > 3"),
        (6, 130, datetime(2026, 9, 1), 117.0, "Daft Punk — другая дата, остаток 2"),
    ]

    print("=" * 70)
    print("РАСШИРЕННОЕ ТЕСТИРОВАНИЕ АЛГОРИТМА СКИДКИ")
    print("=" * 70)

    passed = 0
    for product_id, price, date, expected, comment in test_cases:
        result = calculate_price_with_discount(product_id, price, date)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} Товар {product_id} на {date.date()}: "
              f"{price} → {result} (ожидалось {expected}) — {comment}")

    print("=" * 70)
    print(f"Пройдено: {passed} / {len(test_cases)}")


if __name__ == "__main__":
    run_tests()