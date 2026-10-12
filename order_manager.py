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
#  ПОЗИЦИЯ В СОСТАВ_ЗАКАЗА
# ==========================================================
def add_order_item(order_id, product_id, format_name, quantity, price):
    """Добавляет позицию в состав заказа."""
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
#  ПОЛНЫЙ ЦИКЛ — ЗАКАЗ + ПОЗИЦИИ В ОДНОЙ ТРАНЗАКЦИИ
# ==========================================================
def create_order(client, items):
    """
    Создаёт заказ с несколькими позициями за одну транзакцию.

    :param client: ФИО клиента
    :param items: список кортежей (product_id, format, quantity, price)
    :return: id заказа или None
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        date = datetime.now().strftime("%Y-%m-%d")
        cur.execute(
            "INSERT INTO Заказ (дата, клиент) VALUES (?, ?)",
            (date, client)
        )
        order_id = cur.lastrowid

        for product_id, format_name, quantity, price in items:
            # Проверяем наличие
            cur.execute("SELECT количество FROM Товар WHERE id = ?", (product_id,))
            row = cur.fetchone()

            if not row:
                raise ValueError(f"Товар id={product_id} не найден")

            if row[0] < quantity:
                raise ValueError(f"Недостаточно товара id={product_id}")

            cur.execute(
                "INSERT INTO Состав_заказа "
                "(заказ_id, товар_id, формат, количество, цена) "
                "VALUES (?, ?, ?, ?, ?)",
                (order_id, product_id, format_name, quantity, price)
            )

            # Уменьшаем остаток
            cur.execute(
                "UPDATE Товар SET количество = количество - ? WHERE id = ?",
                (quantity, product_id)
            )

        conn.commit()
        return order_id

    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка создания заказа: {e}")
        return None

    finally:
        conn.close()


# ==========================================================
#  ОБНОВЛЕНИЕ КОЛИЧЕСТВА
# ==========================================================
def update_product_quantity(product_id, new_quantity):
    """Устанавливает новое количество товара."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Товар SET количество = ? WHERE id = ?",
        (new_quantity, product_id)
    )
    conn.commit()
    conn.close()


def decrease_product_quantity(product_id, quantity):
    """Уменьшает количество товара на складе."""
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT количество FROM Товар WHERE id = ?", (product_id,))
        row = cur.fetchone()

        if not row:
            return False

        current = row[0]
        if current is None or current < quantity:
            return False

        cur.execute(
            "UPDATE Товар SET количество = количество - ? WHERE id = ?",
            (quantity, product_id)
        )
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"Ошибка обновления: {e}")
        return False

    finally:
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
#  ВСЕ ЗАКАЗЫ
# ==========================================================
def get_all_orders():
    """Возвращает список всех заказов."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, дата, клиент FROM Заказ ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


# ==========================================================
#  СОСТАВ ЗАКАЗА (JOIN)
# ==========================================================
def get_order_items(order_id):
    """
    Возвращает состав заказа с полной информацией.

    :param order_id: id заказа
    :return: список кортежей
        (id, название, исполнитель, формат, количество, цена)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            Состав_заказа.id,
            Товар.название,
            Товар.исполнитель,
            Состав_заказа.формат,
            Состав_заказа.количество,
            Состав_заказа.цена
        FROM Состав_заказа
        JOIN Товар ON Состав_заказа.товар_id = Товар.id
        WHERE Состав_заказа.заказ_id = ?
        ORDER BY Состав_заказа.id
    """, (order_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


# ==========================================================
#  ИТОГОВАЯ СУММА ЗАКАЗА
# ==========================================================
def get_order_total(order_id):
    """
    Возвращает итоговую сумму заказа.

    :param order_id: id заказа
    :return: сумма (float)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT SUM(количество * цена)
        FROM Состав_заказа
        WHERE заказ_id = ?
    """, (order_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] or 0.0


# ==========================================================
#  ЗАКАЗ ПО ID
# ==========================================================
def get_order_by_id(order_id):
    """
    Возвращает заказ по id.

    :param order_id: id заказа
    :return: кортеж (id, дата, клиент) или None
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, дата, клиент FROM Заказ WHERE id = ?",
                (order_id,))
    row = cur.fetchone()
    conn.close()
    return row


# ==========================================================
#  ЗАДАНИЕ 4 — ИЗМЕНЕНИЕ ДАТЫ ЗАКАЗА
# ==========================================================
def update_order_date(order_id, new_date):
    """
    Обновляет дату заказа.

    :param order_id: id заказа
    :param new_date: новая дата (YYYY-MM-DD)
    :return: True при успехе, False при ошибке
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE Заказ SET дата = ? WHERE id = ?",
            (new_date, order_id)
        )
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"Ошибка обновления даты: {e}")
        return False

    finally:
        conn.close()


# ==========================================================
#  ЗАДАНИЕ 5 — УДАЛЕНИЕ ПОЗИЦИИ
# ==========================================================
def delete_order_item(item_id):
    """
    Удаляет позицию из состава заказа и восстанавливает остаток.

    :param item_id: id позиции
    :return: True при успехе, False при ошибке
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1. Получаем данные позиции
        cur.execute("""
            SELECT товар_id, количество
            FROM Состав_заказа
            WHERE id = ?
        """, (item_id,))
        row = cur.fetchone()

        if not row:
            print(f"[DEBUG] Позиция id={item_id} не найдена")
            return False

        product_id, quantity = row

        # 2. Удаляем позицию
        cur.execute("DELETE FROM Состав_заказа WHERE id = ?", (item_id,))

        # 3. Восстанавливаем остаток
        cur.execute("""
            UPDATE Товар
            SET количество = количество + ?
            WHERE id = ?
        """, (quantity, product_id))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"Ошибка удаления позиции: {e}")
        return False

    finally:
        conn.close()


# ==========================================================
#  ТЕСТИРОВАНИЕ
# ==========================================================
if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ order_manager.py")
    print("=" * 60)

    # Тест 4.5 — обновление даты
    print("\n[1] Проверка update_order_date...")
    order = get_order_by_id(21)
    print(f"    Заказ до: {order}")

    ok = update_order_date(21, "2026-10-08")
    print(f"    update_order_date(21, '2026-10-08') → {ok}")

    order = get_order_by_id(21)
    print(f"    Заказ после: {order}")

    # Вернуть обратно
    update_order_date(21, "2026-10-12")
    print(f"    Дата возвращена: {get_order_by_id(21)}")

    # Тест 5.5 — удаление позиции
    print("\n[2] Проверка delete_order_item...")
    items_before = get_order_items(21)
    print(f"    Позиций до: {len(items_before)}")

    if items_before:
        item_id = items_before[0][0]
        ok = delete_order_item(item_id)
        print(f"    delete_order_item({item_id}) → {ok}")

    items_after = get_order_items(21)
    print(f"    Позиций после: {len(items_after)}")

    print("\n" + "=" * 60)
    print("Тестирование завершено")
    print("=" * 60)