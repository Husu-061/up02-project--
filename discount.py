"""Модуль расчёта скидки."""
from datetime import datetime
import sqlite3
from config import DB_PATH


def get_product_quantity(product_id):
    """Возвращает текущий остаток товара на складе из БД."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT количество FROM Товар WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def calculate_price_with_discount(product_id, price, date=None):
    """
    Рассчитывает цену со скидкой 10% при остатке <= 3.
    
    :param product_id: id товара
    :param price: базовая цена
    :param date: дата расчёта (оставлена для совместимости)
    :return: цена со скидкой или без
    """
    quantity = get_product_quantity(product_id)
    
    if quantity <= 3:
        return price * 0.9  # Скидка 10%
    return price
