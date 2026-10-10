"""Расширенное тестирование каталога товаров."""
import sqlite3
import os
from config import DB_PATH


# ==========================================================
#  ПОДКЛЮЧЕНИЕ К БД
# ==========================================================
def get_products():
    """Возвращает все товары из БД."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Товар ORDER BY id")
    products = cur.fetchall()
    conn.close()
    return products


def test_fields():
    """Проверяет, что все поля товаров на месте (минимум 6 для макета)."""
    products = get_products()
    print(f"Всего товаров: {len(products)}")

    required_count = 6
    errors = 0

    for p in products:
        if len(p) < required_count:
            print(f"❌ Товар id={p[0]}: мало полей ({len(p)})")
            errors += 1

    if errors == 0:
        print("✅ Все товары содержат нужные поля")
    return errors


def test_prices():
    """Проверяет, что у всех товаров есть цена (не None)."""
    products = get_products()
    errors = 0

    for p in products:
        price = p[5]   # индекс цены
        if price is None:
            print(f"❌ Товар id={p[0]}: нет цены (None)")
            errors += 1

    if errors == 0:
        print("✅ У всех товаров есть цена")
    return errors


def test_quantities():
    """Проверяет, что у всех товаров количество ≥ 0."""
    products = get_products()
    errors = 0

    for p in products:
        qty = p[6]   # индекс количества
        if qty is None:
            print(f"❌ Товар id={p[0]}: количество = None")
            errors += 1
        elif qty < 0:
            print(f"❌ Товар id={p[0]}: отрицательное количество ({qty})")
            errors += 1

    if errors == 0:
        print("✅ У всех товаров количество ≥ 0")
    return errors


def test_has_images():
    """Проверяет, что хотя бы у одного товара есть изображение."""
    products = get_products()
    with_image = 0

    for p in products:
        cover = p[7]   # индекс обложки
        if cover:
            with_image += 1

    if with_image > 0:
        print(f"✅ Хотя бы у одного товара есть изображение ({with_image} из {len(products)})")
        return 0
    else:
        print("❌ Ни у одного товара нет изображения")
        return 1


def test_resources():
    """Проверяет наличие ресурсов."""
    errors = 0
    resources = [
        ("resources/picture.png", "Заглушка"),
        ("resources/logo.png", "Логотип"),
    ]
    for path, name in resources:
        if os.path.exists(path):
            print(f"✅ {name} ({path})")
        else:
            print(f"❌ {name} ({path}) — отсутствует")
            errors += 1

    if os.path.exists("images"):
        count = len([f for f in os.listdir("images") if f.endswith(".png")])
        print(f"✅ Папка images/: {count} файлов")
    else:
        print("⚠️ Папка images/ не найдена")

    return errors


def test_large_price():
    """Проверяет товары с ценой > 1 000 000 руб."""
    products = get_products()
    errors = 0
    found = False

    for p in products:
        price = p[5]
        if price is not None and price > 1_000_000:
            found = True
            print(f"⚠️ Товар id={p[0]}: цена {price:,} руб. — очень высокая")
            # Проверяем формат вывода
            formatted = f"{price:,.2f}"
            print(f"   Формат вывода: {formatted} руб.")

    if not found:
        print("✅ Товаров с ценой > 1 000 000 руб. нет")
    return errors


def test_long_titles():
    """Проверяет товары с названием длиннее 100 символов."""
    products = get_products()
    errors = 0
    found = False

    for p in products:
        title = p[3] or ""   # индекс названия
        if len(title) > 100:
            found = True
            print(f"⚠️ Товар id={p[0]}: название длиной {len(title)} символов")
            print(f"   Первые 50: '{title[:50]}...'")

    if not found:
        print("✅ Названий длиннее 100 символов нет")
    return errors


def test_cyrillic_titles():
    """Проверяет товары с кириллическим названием."""
    products = get_products()
    found = 0

    for p in products:
        title = p[3] or ""
        # Проверяем, есть ли кириллица в названии
        if any("а" <= ch.lower() <= "я" for ch in title):
            found += 1

    if found > 0:
        print(f"✅ Найдено товаров с кириллицей в названии: {found}")
    else:
        print("⚠️ Товаров с кириллицей не найдено")
    return 0


def run_all_tests():
    """Запускает все тесты."""
    print("=" * 55)
    print("РАСШИРЕННОЕ ТЕСТИРОВАНИЕ КАТАЛОГА")
    print("=" * 55)

    total_errors = 0

    print("\n[1] Базовые проверки")
    total_errors += test_fields()
    total_errors += test_prices()
    total_errors += test_quantities()
    total_errors += test_has_images()

    print("\n[2] Крайние случаи")
    total_errors += test_large_price()
    total_errors += test_long_titles()
    total_errors += test_cyrillic_titles()

    print("\n[3] Ресурсы")
    total_errors += test_resources()

    print("\n" + "=" * 55)
    if total_errors == 0:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
    else:
        print(f"❌ НАЙДЕНО ОШИБОК: {total_errors}")
    print("=" * 55)


if __name__ == "__main__":
    run_all_tests()