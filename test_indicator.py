"""Тестирование индикатора «много/средне/мало»."""
from catalog import _indicator


def test_indicator():
    """Прогон тестов для индикатора (расширенная версия)."""
    test_cases = [
        # (qty, expected, comment)
        # === Уровень «много» (>20) ===
        (21, "🟢 много", "21 > 20 (граница много)"),
        (25, "🟢 много", "25 > 20"),
        (100, "🟢 много", "большое число"),

        # === Уровень «средне» (6–20) ===
        (20, "🟡 средне", "20 ≤ 20 (граница средне)"),
        (15, "🟡 средне", "15 в диапазоне 6–20"),
        (6, "🟡 средне", "6 > 5 (граница средне)"),

        # === Уровень «мало» (≤5) ===
        (5, "🔴 мало", "5 ≤ 5 (граница мало)"),
        (4, "🔴 мало", "4 ≤ 5"),
        (1, "🔴 мало", "1 ≤ 5"),
        (0, "🔴 мало", "0 ≤ 5 (минимум)"),
    ]

    print("=" * 65)
    print("ТЕСТИРОВАНИЕ ИНДИКАТОРА (3 уровня)")
    print("=" * 65)

    passed = 0
    for qty, expected, comment in test_cases:
        result = _indicator(qty)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} qty={qty}: '{result}' (ожидалось '{expected}') — {comment}")

    print("=" * 65)
    print(f"Пройдено: {passed} / {len(test_cases)}")

    return passed == len(test_cases)


if __name__ == "__main__":
    test_indicator()