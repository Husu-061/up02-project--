"""Модуль расчёта скидки."""
from datetime import datetime, timedelta
import sqlite3
from config import DB_PATH

def get_product_quantity(product_id):
    """Возвращает текущий остаток товара на складе."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT количество FROM Товар WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def calculate_price_with_discount(product_id, price, date=None):
    """Скидка 10% при остатке <= 3."""
    quantity = get_product_quantity(product_id)
    if quantity <= 25:
        return price * 0.9
    return price



def get_previous_month_range(date):
    """Возвращает (начало, конец) предыдущего месяца."""
    first_day = date.replace(day=1)
    last_day_prev = first_day - timedelta(days=1)
    first_day_prev = last_day_prev.replace(day=1)
    return (
        first_day_prev.strftime("%Y-%m-%d"),
        last_day_prev.strftime("%Y-%m-%d")
    )


def has_orders_in_previous_month(product_id, date):
    """Есть ли заказы товара в предыдущем месяце?"""
    start, end = get_previous_month_range(date)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM Заказ "
        "WHERE товар_id = ? AND дата BETWEEN ? AND ?",
        (product_id, start, end)
    )
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def calculate_price_with_discount_orders(product_id, price, date):
    """Скидка 25%, если в прошлом месяце заказов не было."""
    if has_orders_in_previous_month(product_id, date):
        return price
    return price * 0.75