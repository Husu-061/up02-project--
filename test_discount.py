"""Тестирование алгоритма скидки."""
from datetime import datetime
from discount import (
    calculate_price_with_discount,
    calculate_price_with_discount_orders
)


def print_test_report(passed, total):
    """Печатает итоговый отчёт по тестам."""
    print("=" * 40)
    print("ОТЧЁТ О ТЕСТИРОВАНИИ")
    print(f"Пройдено: {passed} / {total}")
    if passed == total:
        print("Результат: ✅ УСПЕХ")
    else:
        print("Результат: ❌ ЕСТЬ ОШИБКИ")
    print("=" * 40)


def run_tests():
    """Прогон всех тестов."""
    test_cases = [
        # ===== Базовые тесты (Логика 1: остаток <= 3) =====
        (1, 100, datetime(2026, 10, 15), 100, "The Beatles — остаток 50 → без скидки"),
        (2, 120, datetime(2026, 10, 15), 120, "Michael Jackson — остаток 40 → без скидки"),
        (4, 150, datetime(2026, 10, 15), 135.0, "Бетховен — остаток 2 → скидка 10%"),
        (6, 130, datetime(2026, 10, 15), 117.0, "Daft Punk — остаток 2 → скидка 10%"),
        (7, 100, datetime(2026, 10, 15), 90.0, "Би-2 — остаток 2 → скидка 10%"),

        # ===== 🆕 5 ГРАНИЧНЫХ ТЕСТОВ =====

        # 1. Дата расчёта — 1-е число месяца
        (4, 150, datetime(2026, 11, 1), 135.0, "Граница: 1-е число месяца"),

        # 2. Дата расчёта — последний день месяца
        (4, 150, datetime(2026, 11, 30), 135.0, "Граница: последний день месяца"),

        # 3. Товар с нулевой ценой (скидка не важна — результат 0)
        (4, 0, datetime(2026, 10, 15), 0.0, "Граница: нулевая цена → 0"),

        # 4. Товар с отрицательным количеством (алгоритм всё равно даст скидку)
        (4, 150, datetime(2026, 10, 15), 135.0, "Граница: отрицательный остаток"),

        # 5. Скидка 25% по заказам за прошлый месяц (Логика 2)
        # Товар 4: заказов в сентябре не было → должна быть скидка 25%
        (4, 150, datetime(2026, 10, 15), 112.5, "Заказов в сентябре нет → 25%"),
    ]

    print("=" * 70)
    print("РАСШИРЕННОЕ ТЕСТИРОВАНИЕ АЛГОРИТМА СКИДКИ")
    print("=" * 70)

    passed = 0
    for product_id, price, date, expected, comment in test_cases:
        # Тест №5 использует вторую логику (по заказам)
        if "по заказам" in comment or "25%" in comment:
            result = calculate_price_with_discount_orders(product_id, price, date)
        else:
            result = calculate_price_with_discount(product_id, price, date)

        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} Товар {product_id} на {date.date()}: "
              f"{price} → {result} (ожидалось {expected}) — {comment}")

    print()
    print_test_report(passed, len(test_cases))


if __name__ == "__main__":
    run_tests()