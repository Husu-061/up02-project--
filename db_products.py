"""Загрузка товаров из БД в объекты класса Product."""
import sqlite3
from models import Product  # Убедитесь, что этот класс уже написан!


def get_all_products():
    """Возвращает список объектов Product из БД (все товары)."""
    conn = sqlite3.connect("databases/db_variant_23.db")
    cur = conn.cursor()
    
    # Порядок полей по вашему скриншоту: ROWID | id | жанр | исполнитель | название |
    # длительность | цена | количество | обложка
    cur.execute("SELECT * FROM Товар ORDER BY название") 
    rows = cur.fetchall()
    conn.close()

    products = []
    for row in rows:
        product = Product(
            product_id=row[0],   # id товара ✅
            genre=row[1],       # жанр ✅
            artist=row[2],      # исполнитель ✅
            title=row[3],       # название композиции ✅
            duration=row[4],     # длительность ✅
            price=row[5],        
            quantity=row[6]      
        )
        products.append(product)
    return products


def get_products_by_genre(genre):
    """
    Возвращает список объектов Product по жанру.
    ⚠️ В вашей таблице это поле называется не категория, а жанр!
    """
    conn = sqlite3.connect("databases/db_variant_23.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM Товар WHERE жанр = ?", (genre,))
    rows = cur.fetchall()
    conn.close()

    products = []
    for row in rows:
        product = Product(
            product_id=row[0],
            genre=row[1],
            artist=row[2],
            title=row[3],
            duration=row[4],
            price=row[5],
            quantity=row[6]
        )
        products.append(product)
    return products



def get_products_low_stock():
    """Возвращает товары с количеством ≤ 5."""
    conn = sqlite3.connect("databases/db_variant_23.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM Товар WHERE количество <= 30")
    rows = cur.fetchall()
    conn.close()

    products = []
    for row in rows:
        product = Product(
            product_id=row[0],
            genre=row[1],
            artist=row[2],
            title=row[3],
            duration=row[4],
            price=row[5],
            quantity=row[6]
        )
        products.append(product)
    return products


def print_catalog_with_highlight(products):
    """
    Выводит каталог с подсветкой для товаров ≤5.
    Использует метод info() вашего класса.
    """
    print(f"\n{'=' * 70}")
    print(f"КАТАЛОГ ({len(products)} позиций)")
    print("=" * 70)

    for p in products:
        highlight = "🛑 НИЗКИЙ ОСТАТОК!" if p.quantity <= 30 else ""
        print(f"{highlight} {p.info()}")  # Используем ваш готовый метод info()

    print("=" * 70)


if __name__ == "__main__":
    print("1. Все товары:")
    print_catalog_with_highlight(get_all_products())

    print("\n2. Товары жанра «Джаз»:")
    print_catalog_with_highlight(get_products_by_genre("Джаз"))

    print("\n3. Товары с низким остатком (≤30):")
    print_catalog_with_highlight(get_products_low_stock())