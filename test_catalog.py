"""Тестирование каталога (интеграционные тесты с БД)."""
import sqlite3
import os
from config import DB_PATH


def get_all_products():
    """Возвращает все товары из БД."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Товар ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


# ==========================================================
#  ТЕСТЫ
# ==========================================================
def test_db_available():
    """БД доступна — get_all_products() возвращает список."""
    try:
        products = get_all_products()
        return isinstance(products, list)
    except Exception as e:
        print(f"❌ БД недоступна: {e}")
        return False


def test_products_count():
    """Товары загружены — количество > 0."""
    products = get_all_products()
    return len(products) > 0


def test_product_fields():
    """У всех товаров минимум 8 полей."""
    products = get_all_products()
    for p in products:
        if len(p) < 8:
            print(f"❌ Товар id={p[0]}: мало полей ({len(p)})")
            return False
    return True


def test_prices_are_numbers():
    """Все цены — числа (int или float)."""
    products = get_all_products()
    for p in products:
        if not isinstance(p[5], (int, float)):
            print(f"❌ Товар id={p[0]}: цена не число ({p[5]})")
            return False
    return True


def test_quantity_not_negative():
    """Количество не отрицательное."""
    products = get_all_products()
    for p in products:
        if p[6] is not None and p[6] < 0:
            print(f"❌ Товар id={p[0]}: отрицательное количество ({p[6]})")
            return False
    return True


# ==========================================================
#  НОВЫЙ ТЕСТ (Задание 6.6)
# ==========================================================
def test_names_not_empty():
    """Проверяет, что у всех товаров есть название (не пустое)."""
    products = get_all_products()
    for p in products:
        # p[3] — название в вашей БД
        if not p[3]:
            print(f"❌ Товар id={p[0]}: пустое название")
            return False
    return True


def test_images_available():
    """Проверяет, что хотя бы у одного товара есть обложка."""
    products = get_all_products()
    count = sum(1 for p in products if p[7])
    if count > 0:
        print(f"   Обложек в БД: {count} из {len(products)}")
        return True
    return False


# ==========================================================
#  ЗАПУСК ВСЕХ ТЕСТОВ
# ==========================================================
def run_all_tests():
    """Прогон всех тестов каталога."""
    tests = [
        ("БД доступна", test_db_available),
        ("Товары загружены", test_products_count),
        ("У всех товаров нужные поля", test_product_fields),
        ("Все цены — числа", test_prices_are_numbers),
        ("Количество не отрицательное", test_quantity_not_negative),
        ("У всех товаров есть название", test_names_not_empty),         # ← новый
        ("Хотя бы одна обложка есть", test_images_available),           # ← бонус
    ]

    print("=" * 60)
    print("ТЕСТИРОВАНИЕ КАТАЛОГА")
    print("=" * 60)

    passed = 0
    for name, func in tests:
        result = func()
        status = "✅" if result else "❌"
        if result:
            passed += 1
        print(f"{status} {name}")

    print("=" * 60)
    print(f"Пройдено: {passed} / {len(tests)}")

    return passed == len(tests)


if __name__ == "__main__":
    run_all_tests()