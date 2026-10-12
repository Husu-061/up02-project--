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
#  ЗАДАНИЕ 5.3 — CREATE_ORDER С ТРАНЗАКЦИЕЙ
# ==========================================================
def create_order(client, items):
    """
    Создаёт заказ с несколькими позициями ЗА ОДНУ ТРАНЗАКЦИЮ.

    Три действия:
    1. Создаёт «шапку» заказа.
    2. Добавляет все позиции в Состав_заказа.
    3. Уменьшает остатки в Товар.

    При ошибке — rollback откатывает ВСЁ.

    :param client: ФИО клиента
    :param items: список кортежей
        (product_id, format, quantity, price)
    :return: id заказа или None при ошибке
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # ===== 1. Создаём заказ =====
        date = datetime.now().strftime("%Y-%m-%d")
        cur.execute(
            "INSERT INTO Заказ (дата, клиент) VALUES (?, ?)",
            (date, client)
        )
        order_id = cur.lastrowid

        # ===== 2. Обрабатываем каждую позицию =====
        for product_id, format_name, quantity, price in items:
            # 2.1. Проверяем наличие товара
            cur.execute(
                "SELECT количество FROM Товар WHERE id = ?",
                (product_id,)
            )
            row = cur.fetchone()

            if not row:
                raise ValueError(f"Товар id={product_id} не найден")

            if row[0] < quantity:
                raise ValueError(
                    f"Недостаточно товара id={product_id}: "
                    f"в наличии {row[0]}, запрошено {quantity}"
                )

            # 2.2. Добавляем позицию в Состав_заказа
            cur.execute(
                "INSERT INTO Состав_заказа "
                "(заказ_id, товар_id, формат, количество, цена) "
                "VALUES (?, ?, ?, ?, ?)",
                (order_id, product_id, format_name, quantity, price)
            )

            # 2.3. Уменьшаем остаток товара
            cur.execute(
                "UPDATE Товар SET количество = количество - ? WHERE id = ?",
                (quantity, product_id)
            )

        # ===== 3. Фиксируем ВСЁ =====
        conn.commit()
        return order_id

    except Exception as e:
        # Откат всех изменений при любой ошибке
        conn.rollback()
        print(f"❌ Ошибка создания заказа: {e}")
        return None

    finally:
        # Гарантированно закрываем соединение
        conn.close()


# ==========================================================
#  ПРОСТОЕ ОБНОВЛЕНИЕ КОЛИЧЕСТВА (устанавливает значение)
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


# ==========================================================
#  DECREASE_PRODUCT_QUANTITY (уменьшение на N)
# ==========================================================
def decrease_product_quantity(product_id, quantity):
    """
    Уменьшает количество товара на складе.

    :param product_id: id товара
    :param quantity: на сколько уменьшить
    :return: True при успехе, False при ошибке
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT количество FROM Товар WHERE id = ?", (product_id,))
        row = cur.fetchone()

        if not row:
            print(f"[DEBUG] Товар id={product_id} не найден")
            return False

        current = row[0]
        if current is None or current < quantity:
            print(f"[DEBUG] Недостаточно товара: {current} < {quantity}")
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
#  ТЕСТИРОВАНИЕ
# ==========================================================
if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ order_manager.py")
    print("=" * 60)

    print("\n[1] Проверка create_order с транзакцией...")
    qty1_before = get_product_quantity(1)
    qty2_before = get_product_quantity(2)
    print(f"    Товар 1 до: {qty1_before} шт.")
    print(f"    Товар 2 до: {qty2_before} шт.")

    items = [
        (1, "MP3",  2, 100),
        (2, "FLAC", 1, 120),
    ]
    order_id = create_order("Иванов Иван Иванович", items)
    print(f"    Заказ создан: id={order_id}")

    qty1_after = get_product_quantity(1)
    qty2_after = get_product_quantity(2)
    print(f"    Товар 1 после: {qty1_after} шт. (-{qty1_before - qty1_after})")
    print(f"    Товар 2 после: {qty2_after} шт. (-{qty2_before - qty2_after})")

    print("\n[2] Проверка rollback — недостаточно товара...")
    qty1_before2 = get_product_quantity(1)
    bad_items = [
        (1, "MP3",  1, 100),
        (4, "MP3", 9999, 150),   # Не хватит
    ]
    bad_order = create_order("Тестов Тест", bad_items)
    print(f"    Заказ: {bad_order} (ожидалось None)")

    qty1_after2 = get_product_quantity(1)
    print(f"    Товар 1 после ошибки: {qty1_after2} шт. "
          f"(ожидалось {qty1_before2})")

    if qty1_before2 == qty1_after2:
        print("    ✅ Rollback сработал — остаток не изменился")
    else:
        print("    ❌ Rollback не сработал!")

    print("\n" + "=" * 60)
    print("Тестирование завершено")
    print("=" * 60)


def get_all_orders():
    """
    Возвращает список всех заказов.

    :return: список кортежей (id, дата, клиент)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, дата, клиент FROM Заказ ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows



def get_order_items(order_id):
    """
    Возвращает состав заказа.

    :param order_id: id заказа
    :return: список кортежей
        (id, название, исполнитель, формат, количество, цена)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT Состав_заказа.id,
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
#  ЗАДАНИЕ 4 — ИТОГОВАЯ СУММА ЗАКАЗА
# ==========================================================
def get_order_total(order_id):
    """
    Возвращает итоговую сумму заказа.

    :param order_id: id заказа
    :return: сумма (float)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT SUM(количество * цена) FROM Состав_заказа "
        "WHERE заказ_id = ?",
        (order_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row and row[0] else 0