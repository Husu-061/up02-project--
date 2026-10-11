"""Тестовый запуск формы просмотра (с отладкой)."""
import tkinter as tk
import sqlite3
import traceback

from config import DB_PATH
from view_form import ViewForm


def main():
    print("[1] Создаём root...")
    root = tk.Tk()
    root.title("Главное окно (скрыто)")
    root.geometry("300x200")
    #root.withdraw()   # ← скрываем root; ViewForm показывается через deiconify()

    print("[2] Загружаем товар из БД...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM Товар LIMIT 1")
        product = cur.fetchone()
        conn.close()
        print(f"[3] Загружен товар: {product}")
    except Exception as e:
        print(f"[ERROR] Ошибка БД: {e}")
        traceback.print_exc()
        return

    if not product:
        print("[ERROR] В БД нет товаров!")
        return

    def on_add(p):
        print(f"[DEBUG] Добавляем в заказ: {p[3]}")

    print("[4] Создаём ViewForm...")
    try:
        form = ViewForm(root, product, on_add_to_order=on_add)
        print("[5] ViewForm создан")
    except Exception as e:
        print(f"[ERROR] Ошибка ViewForm: {e}")
        traceback.print_exc()
        return

    print("[6] Запускаем mainloop...")
    root.mainloop()
    print("[7] mainloop завершён")


if __name__ == "__main__":
    main()