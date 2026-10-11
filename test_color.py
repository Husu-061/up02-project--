"""Тестирование подсветки карточек."""
from catalog import _get_card_color
from styles import COLOR_HIGHLIGHT, COLOR_MAIN_BG, COLOR_SECONDARY_BG


def test_color():
    """Прогон тестов для подсветки (с учётом чередования фона)."""
    test_cases = [
        # (qty, index, expected, comment)

        # ===== Подсветка (qty ≤ 3) — независимо от индекса =====
        (3, 0, COLOR_HIGHLIGHT, "3 ≤ 3 (граница!) — подсветка"),
        (3, 1, COLOR_HIGHLIGHT, "3 ≤ 3 (граница), нечётный idx — подсветка"),
        (2, 0, COLOR_HIGHLIGHT, "2 ≤ 3 — подсветка"),
        (0, 0, COLOR_HIGHLIGHT, "0 ≤ 3 — подсветка (минимум)"),

        # ===== Без подсветки (qty > 3) — чередование =====
        (4, 0, COLOR_MAIN_BG,      "4 > 3, чётный idx → белый"),
        (5, 0, COLOR_MAIN_BG,      "5 > 3, чётный idx → белый"),
        (10, 0, COLOR_MAIN_BG,     "10 > 3, чётный idx → белый"),
        (4, 1, COLOR_SECONDARY_BG, "4 > 3, нечётный idx → зелёный"),
        (5, 1, COLOR_SECONDARY_BG, "5 > 3, нечётный idx → зелёный"),
        (10, 2, COLOR_MAIN_BG,     "10 > 3, чётный idx → белый"),

        # ===== 2 новых теста (Задание 5.6) =====
        (100, 0, COLOR_MAIN_BG,   "большое число → без подсветки"),
        (-1,  0, COLOR_HIGHLIGHT, "отрицательное → подсветка (≤ 3)"),
    ]

    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ПОДСВЕТКИ (с чередованием фона)")
    print("=" * 70)

    passed = 0
    for qty, index, expected, comment in test_cases:
        result = _get_card_color(qty, index)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} qty={qty:>4}, idx={index}: {result} "
              f"(ожидалось {expected}) — {comment}")

    print("=" * 70)
    print(f"Пройдено: {passed} / {len(test_cases)}")

    return passed == len(test_cases)


if __name__ == "__main__":
    test_color()