"""Тестирование подсветки товаров (с учётом чередования фона)."""
from catalog import _get_card_color
from styles import COLOR_HIGHLIGHT, COLOR_MAIN_BG, COLOR_SECONDARY_BG


def test_highlight():
    """Прогон тестов для подсветки."""
    test_cases = [
        # (qty, index, expected, comment)

        # ===== Подсветка (qty ≤ 3) =====
        (0,  0, COLOR_HIGHLIGHT, "0 ≤ 3 → подсветка (минимум)"),
        (1,  0, COLOR_HIGHLIGHT, "1 ≤ 3 → подсветка"),
        (2,  0, COLOR_HIGHLIGHT, "2 ≤ 3 → подсветка"),
        (3,  0, COLOR_HIGHLIGHT, "3 ≤ 3 → подсветка (граница)"),
        (3,  1, COLOR_HIGHLIGHT, "3 ≤ 3, нечётный индекс → подсветка"),
        (2,  5, COLOR_HIGHLIGHT, "2 ≤ 3, любой индекс → подсветка"),

        # ===== Без подсветки (qty > 3) — чередование =====
        (4,  0, COLOR_MAIN_BG,      "4 > 3, чётный idx → белый"),
        (4,  1, COLOR_SECONDARY_BG, "4 > 3, нечётный idx → зелёный"),
        (5,  0, COLOR_MAIN_BG,      "5 > 3, чётный idx → белый"),
        (5,  1, COLOR_SECONDARY_BG, "5 > 3, нечётный idx → зелёный"),
        (10, 0, COLOR_MAIN_BG,      "10 > 3, чётный idx → белый"),
        (10, 2, COLOR_MAIN_BG,      "10 > 3, чётный idx → белый"),
        (50, 3, COLOR_SECONDARY_BG, "50 > 3, нечётный idx → зелёный"),

        # ===== 3 новых теста (ДЗ) =====
        (1000, 0, COLOR_MAIN_BG,      "1000 > 3 → нет подсветки"),
        (-1,   0, COLOR_HIGHLIGHT,    "-1 ≤ 3 → подсветка (отрицательное)"),
        (3,    5, COLOR_HIGHLIGHT,    "3 — повторная граница, любой idx"),
    ]

    print("=" * 75)
    print("РАСШИРЕННОЕ ТЕСТИРОВАНИЕ ПОДСВЕТКИ")
    print("=" * 75)

    passed = 0
    for qty, index, expected, comment in test_cases:
        result = _get_card_color(qty, index)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} qty={qty:>5}, idx={index}: {result} "
              f"(ожидалось {expected}) — {comment}")

    print("=" * 75)
    print(f"Пройдено: {passed} / {len(test_cases)}")

    return passed == len(test_cases)


if __name__ == "__main__":
    test_highlight()