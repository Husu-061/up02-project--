"""Загрузка заказов из БД в объекты класса Order."""
import sqlite3
from models import Order  
from db_products import get_all_products


DB_PATH = "databases/db_variant_23.db"


def load_products_into_orders(orders: list[Order], products):

    for o in orders:
        matching_product = next(
            (p for p in products if p.product_id == o.product_id),
            None  # Если не нашли — будет None
        )
        
        o.product = matching_product  
    
    return orders


def get_all_orders():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    

    cur.execute("SELECT * FROM Заказ ORDER BY дата DESC")
    rows = cur.fetchall()
    conn.close()

    orders = []
    for row in rows:
        order = Order(
            order_id=row[0],
            date=row[1],          # Дата заказа
            client=row[2],        # Клиент
            product_id=row[3],    # ЧИСЛОВОЙ идентификатор товара
            quantity=row[4]       # Количество
        )
        orders.append(order)



    all_products = get_all_products() 
    return load_products_into_orders(orders, all_products)


def print_orders(orders):
    """Печатает информацию о каждом заказе красиво."""
    print(f"\n{'=' * 65}")
    print(f"❗ ЗАКАЗЫ ({len(orders)} позиций)")
    print("=" * 65)

    for o in orders:
        highlight = "🛑 НЕТ В НАЛИЧИИ!" if not hasattr(o, 'product') else ""

        price_str = f"{o.total():.2f} ₽" if o.total() is not None else "-"
        name = getattr(o.product, "title", f"Товар №{o.product_id}") \
               if hasattr(o, 'product') else f"Товар №{o.product_id}"

        print(f"{highlight}\t{o.date}: {o.client}, {name} × {o.quantity}")
        print(f"\tЦена за единицу: {getattr(o.product, 'price', '-')} ₽")
        print(f"\tОбщая сумма:     {price_str}")

    print("-" * 65)


if __name__ == "__main__":
    orders = get_all_orders()
    print_orders(orders)