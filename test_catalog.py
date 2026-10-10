"""Проверка вывода полей каталога."""
import sqlite3
from config import DB_PATH


def test_fields():
    """Проверяет, что все поля товаров на месте (минимум 6 для макета)."""
    # Подключаемся к БД
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Товар ORDER BY id")
    products = cur.fetchall()
    conn.close()

    print(f"Всего товаров: {len(products)}")

    required_count = 6   # минимум полей для макета
    errors = 0

    for p in products:
        if len(p) < required_count:
            print(f"❌ Товар id={p[0]}: мало полей ({len(p)})")
            errors += 1

    if errors == 0:
        print("✅ Все товары содержат нужные поля")
    else:
        print(f"❌ Найдено ошибок: {errors}")

    return errors


def test_prices():
    """Проверяет, что у всех товаров корректная цена (не None, не отрицательная)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, исполнитель, цена FROM Товар ORDER BY id")
    products = cur.fetchall()
    conn.close()

    print("\n--- Проверка цен ---")
    errors = 0
    for pid, artist, price in products:
        if price is None:
            print(f"❌ Товар id={pid} ({artist}): цена = None")
            errors += 1
        elif price < 0:
            print(f"❌ Товар id={pid} ({artist}): отрицательная цена ({price})")
            errors += 1
        else:
            print(f"✅ Товар id={pid}: {price} руб.")

    if errors == 0:
        print("✅ Все цены корректны")
    return errors


def test_quantities():
    """Проверяет индикаторы количества."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, исполнитель, количество FROM Товар ORDER BY id")
    products = cur.fetchall()
    conn.close()

    print("\n--- Проверка количеств ---")
    for pid, artist, qty in products:
        # Индикатор
        if qty is None:
            indicator = "❌ None"
        elif qty > 20:
            indicator = "🟢 много"
        elif qty > 5:
            indicator = "🟡 средне"
        else:
            indicator = "🔴 мало"

        # Подсветка
        highlight = "🔴 красный" if (qty is not None and qty <= 3) else "⚪ обычный"
        print(f"✅ id={pid} ({artist}): qty={qty}, {indicator}, фон: {highlight}")


def test_resources():
    """Проверяет наличие всех ресурсов."""
    import os
    print("\n--- Проверка ресурсов ---")

    resources = [
        ("resources/picture.png", "Заглушка"),
        ("resources/logo.png", "Логотип"),
        ("resources/icon.ico", "Иконка"),
    ]

    for path, name in resources:
        if os.path.exists(path):
            print(f"✅ {name} ({path})")
        else:
            print(f"❌ {name} ({path}) — ОТСУТСТВУЕТ")

    # Папка images
    if os.path.exists("images"):
        count = len([f for f in os.listdir("images") if f.endswith(".png")])
        print(f"✅ Папка images/: {count} обложек")
    else:
        print("⚠️ Папка images/ не найдена")


def run_all_tests():
    """Запускает все тесты."""
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ КАТАЛОГА ТОВАРОВ")
    print("=" * 50)

    total_errors = 0
    total_errors += test_fields()
    total_errors += test_prices()
    test_quantities()
    test_resources()

    print("\n" + "=" * 50)
    if total_errors == 0:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
    else:
        print(f"❌ НАЙДЕНО ОШИБОК: {total_errors}")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()