"""Тестирование каталога (интеграционные тесты с БД)."""
import sqlite3
from config import DB_PATH


def get_all_products():
    """Возвращает все товары из БД."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Товар ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def test_db_available():
    try:
        products = get_all_products()
        return isinstance(products, list)
    except Exception as e:
        print(f"❌ БД недоступна: {e}")
        return False


def test_products_count():
    products = get_all_products()
    return len(products) > 0


def test_product_fields():
    products = get_all_products()
    for p in products:
        if len(p) < 8:
            print(f"❌ Товар id={p[0]}: мало полей ({len(p)})")
            return False
    return True


def test_prices_are_numbers():
    products = get_all_products()
    for p in products:
        if not isinstance(p[5], (int, float)):
            print(f"❌ Товар id={p[0]}: цена не число ({p[5]})")
            return False
    return True


def test_quantity_not_negative():
    products = get_all_products()
    for p in products:
        if p[6] is not None and p[6] < 0:
            print(f"❌ Товар id={p[0]}: отрицательное количество ({p[6]})")
            return False
    return True


def test_names_not_empty():
    products = get_all_products()
    for p in products:
        if not p[3]:
            print(f"❌ Товар id={p[0]}: пустое название")
            return False
    return True


def test_has_images():
    """Хотя бы у одного товара есть изображение (обложка в БД)."""
    products = get_all_products()
    with_images = [p for p in products if p[7]]

    if len(with_images) > 0:
        print(f"   Товаров с обложкой: {len(with_images)} из {len(products)}")
        return True
    else:
        print(f"❌ Ни у одного товара нет обложки")
        return False


def run_all_tests():
    tests = [
        ("БД доступна", test_db_available),
        ("Товары загружены", test_products_count),
        ("У всех товаров нужные поля", test_product_fields),
        ("Все цены — числа", test_prices_are_numbers),
        ("Количество не отрицательное", test_quantity_not_negative),
        ("У всех товаров есть название", test_names_not_empty),
        ("Хотя бы у одного есть изображение", test_has_images),   # ← новый
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