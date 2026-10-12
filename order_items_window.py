"""Окно состава заказа."""
import tkinter as tk
from tkinter import ttk, messagebox

from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, FONT_SIZE_HEADER, font
)
import order_manager as om


class OrderItemsWindow:
    """Окно состава заказа."""

    def __init__(self, parent, order_id):
        """
        Инициализация окна.

        :param parent: родительское окно
        :param order_id: id заказа
        """
        self.order_id = order_id

        self.window = tk.Toplevel(parent)
        self.window.title(f"Состав заказа №{order_id}")
        self.window.geometry("850x500")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.window.transient(parent)

        # ЯВНО показываем окно
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

        # Закрытие по Esc
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        self.build_ui()
        self.load_items()

    # ==========================================================
    #  ПОСТРОЕНИЕ ИНТЕРФЕЙСА
    # ==========================================================
    def build_ui(self):
        """Строит интерфейс окна."""
        # ===== Шапка =====
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text=f"СОСТАВ ЗАКАЗА №{self.order_id}",
                 font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(pady=15)

        # ===== Таблица позиций =====
        # У вас поле "формат" вместо "размер"
        columns = ("artist", "name", "format", "quantity", "price", "total")
        self.tree = ttk.Treeview(self.window, columns=columns,
                                 show="headings", height=10)

        self.tree.heading("artist",   text="Исполнитель")
        self.tree.heading("name",     text="Товар")
        self.tree.heading("format",   text="Формат")
        self.tree.heading("quantity", text="Кол-во")
        self.tree.heading("price",    text="Цена")
        self.tree.heading("total",    text="Сумма")

        self.tree.column("artist",   width=150, anchor="w")
        self.tree.column("name",     width=200, anchor="w")
        self.tree.column("format",   width=80,  anchor="center")
        self.tree.column("quantity", width=70,  anchor="center")
        self.tree.column("price",    width=100, anchor="e")
        self.tree.column("total",    width=100, anchor="e")

        # Скроллбар
        scrollbar = ttk.Scrollbar(self.window, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="top", fill="both", expand=True,
                       padx=20, pady=(20, 10))
        scrollbar.pack(side="right", fill="y", pady=(20, 10), padx=(0, 5))

        # ===== Итоговая сумма =====
        self.total_label = tk.Label(self.window, text="",
                                     font=font(FONT_SIZE_HEADER, bold=True),
                                     bg=COLOR_MAIN_BG, fg="black")
        self.total_label.pack(pady=5)

        # ===== Кнопки =====
        btn_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="← Назад",
                  command=self.window.destroy,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=15, pady=5,
                  cursor="hand2").pack(side="right", padx=20)

    # ==========================================================
    #  ЗАГРУЗКА ПОЗИЦИЙ (Задание 6.3)
    # ==========================================================
    def load_items(self):
        """Загружает позиции заказа из БД."""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            items = om.get_order_items(self.order_id)
            total = 0.0

            for item in items:
                # item = (id, название, исполнитель, формат, кол-во, цена, сумма)
                name    = item[1]
                artist  = item[2]
                fmt     = item[3]
                qty     = item[4]
                price   = item[5]

                item_total = qty * price
                total += item_total

                self.tree.insert("", tk.END, values=(
                    artist, name, fmt, qty,
                    f"{price:.2f}", f"{item_total:.2f}"
                ))

            self.total_label.config(text=f"Итого: {total:.2f} руб.")

        except Exception as e:
            messagebox.showerror("Ошибка",
                                 f"Не удалось загрузить состав:\n{e}")