"""Работа с заказами (музыкальный магазин)."""
import sqlite3
from datetime import datetime
from config import DB_PATH


def get_connection():
    """Соединение с БД."""
    return sqlite3.connect(DB_PATH)


def add_order_to_db(client, product_id, quantity):
    """Добавляет новый заказ в БД."""
    conn = get_connection()
    cur = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d")

    cur.execute(
        "INSERT INTO Заказ (дата, клиент, товар_id, количество) "
        "VALUES (?, ?, ?, ?)",
        (date, client, product_id, quantity)
    )

    conn.commit()
    order_id = cur.lastrowid
    conn.close()

    return order_id


def update_product_quantity(product_id, new_quantity):
    """Обновляет количество товара в БД."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE Товар SET количество = ? WHERE id = ?",
        (new_quantity, product_id)
    )

    conn.commit()
    conn.close()



def get_last_order_id():
    """Возвращает id последнего заказа."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT MAX(id) FROM Заказ")
    row = cur.fetchone()
    conn.close()

    return row[0] if row and row[0] is not None else None



def get_product_quantity(product_id):
    """Возвращает количество товара по id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT количество FROM Товар WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def create_order(client, product_id, quantity):
    """Полный цикл: проверка → создание → обновление остатка."""
    current_qty = get_product_quantity(product_id)

    if current_qty < quantity:
        return (False, f"Недостаточно товара: в наличии {current_qty} шт.")

    order_id = add_order_to_db(client, product_id, quantity)
    if order_id is None:
        return (False, "Не удалось создать заказ в БД")

    new_qty = current_qty - quantity
    update_product_quantity(product_id, new_qty)

    return (True, order_id)