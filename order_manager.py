"""Работа с заказами (музыкальный магазин)."""
import sqlite3
from datetime import datetime
from config import DB_PATH


def get_connection():
    """Соединение с БД."""
    return sqlite3.connect(DB_PATH)


# ==========================================================
#  ЗАКАЗ — «ШАПКА» (только дата + клиент)
# ==========================================================
def add_order_to_db(client, date=None):
    """Создаёт заказ (только дата + клиент)."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Заказ (дата, клиент) VALUES (?, ?)",
        (date, client)
    )
    conn.commit()
    order_id = cur.lastrowid
    conn.close()
    return order_id


# ==========================================================
#  ЗАДАНИЕ 6.2 — ДОБАВЛЕНИЕ ПОЗИЦИИ В СОСТАВ_ЗАКАЗА
# ==========================================================
def add_order_item(order_id, product_id, format_name, quantity, price):
    """
    Добавляет позицию в состав заказа.

    :param order_id: id заказа
    :param product_id: id товара
    :param format_name: формат файла (MP3/FLAC/WAV)
    :param quantity: количество
    :param price: цена за единицу на момент заказа
    :return: id позиции или None
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO Состав_заказа "
            "(заказ_id, товар_id, формат, количество, цена) "
            "VALUES (?, ?, ?, ?, ?)",
            (order_id, product_id, format_name, quantity, price)
        )
        conn.commit()
        item_id = cur.lastrowid
        conn.close()

        return item_id

    except Exception as e:
        print(f"[DEBUG] Ошибка add_order_item: {e}")
        return None


# ==========================================================
#  ЗАДАНИЕ 6.4 — КОМПЛЕКСНАЯ ФУНКЦИЯ create_order
# ==========================================================
def create_order(client, items):
    """
    Создаёт заказ с несколькими позициями за одну транзакцию.

    :param client: ФИО клиента
    :param items: список кортежей (product_id, format, quantity, price)
    :return: id заказа или None при ошибке
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1. Создаём «шапку» заказа
        date = datetime.now().strftime("%Y-%m-%d")
        cur.execute(
            "INSERT INTO Заказ (дата, клиент) VALUES (?, ?)",
            (date, client)
        )
        order_id = cur.lastrowid

        # 2. Добавляем все позиции
        for product_id, format_name, quantity, price in items:
            cur.execute(
                "INSERT INTO Состав_заказа "
                "(заказ_id, товар_id, формат, количество, цена) "
                "VALUES (?, ?, ?, ?, ?)",
                (order_id, product_id, format_name, quantity, price)
            )

        # 3. Фиксируем только если всё прошло успешно
        conn.commit()
        return order_id

    except Exception as e:
        conn.rollback()
        print(f"Ошибка создания заказа: {e}")
        return None

    finally:
        conn.close()


# ==========================================================
#  ОБНОВЛЕНИЕ КОЛИЧЕСТВА ТОВАРА
# ==========================================================
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


# ==========================================================
#  ВСПОМОГАТЕЛЬНЫЕ
# ==========================================================
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


# ==========================================================
#  ТЕСТИРОВАНИЕ
# ==========================================================
if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ order_manager.py")
    print("=" * 60)

    print("\n[1] Проверка add_order_item...")
    order_id = add_order_to_db("Тестов Тест")
    print(f"    Заказ создан: id={order_id}")

    item_id = add_order_item(order_id, 1, "MP3", 2, 100)
    print(f"    Позиция добавлена: id={item_id}")

    print("\n[2] Проверка create_order с несколькими позициями...")
    items = [
        (1, "MP3",  2, 100),   # Hey Jude
        (2, "FLAC", 1, 120),   # Billie Jean
        (5, "WAV",  3, 110),   # Lose Yourself
    ]
    multi_id = create_order("Иванов Иван Иванович", items)
    print(f"    Заказ с {len(items)} позициями: id={multi_id}")

    print("\n" + "=" * 60)
    print("Тестирование завершено")
    print("=" * 60)