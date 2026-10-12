"""Окно списка заказов (для Менеджера/Администратора)."""
import tkinter as tk
from tkinter import ttk, messagebox

from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_HEADER, FONT_SIZE_TITLE, font
)
import order_manager as om


class OrdersWindow:
    """Окно списка заказов."""

    def __init__(self, parent, user=None):
        """
        :param parent: родительское окно
        :param user: (id, логин, фио, роль) — 4 элемента
        """
        self.user = user

        self.window = tk.Toplevel(parent)
        self.window.title("Список заказов")
        self.window.geometry("950x550")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.window.transient(parent)

        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        self.build_ui()
        self.load_orders()

    # ==========================================================
    #  ИНТЕРФЕЙС
    # ==========================================================
    def build_ui(self):
        # ===== Шапка =====
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="СПИСОК ЗАКАЗОВ",
                 font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(pady=15)

        # ===== Таблица =====
        columns = ("id", "date", "client", "total")
        self.tree = ttk.Treeview(self.window, columns=columns,
                                 show="headings", height=15)

        self.tree.heading("id",     text="№")
        self.tree.heading("date",   text="Дата")
        self.tree.heading("client", text="Клиент")
        self.tree.heading("total",  text="Сумма, руб.")

        self.tree.column("id",     width=60,  anchor="center")
        self.tree.column("date",   width=120, anchor="center")
        self.tree.column("client", width=400, anchor="w")
        self.tree.column("total",  width=120, anchor="e")

        scrollbar = ttk.Scrollbar(self.window, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="top", fill="both", expand=True,
                       padx=20, pady=(20, 10))
        scrollbar.pack(side="right", fill="y", pady=(20, 10), padx=(0, 5))

        self.tree.bind("<Double-1>", self.on_order_select)

        # ===== Кнопки =====
        btn_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="👁 Просмотр состава",
                  command=self.on_order_select,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=15, pady=5,
                  cursor="hand2").pack(side="left", padx=20)

        tk.Button(btn_frame, text="🔄 Обновить",
                  command=self.load_orders,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=15, pady=5,
                  cursor="hand2").pack(side="left", padx=10)

        tk.Button(btn_frame, text="← Назад",
                  command=self.window.destroy,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=15, pady=5,
                  cursor="hand2").pack(side="right", padx=20)

    # ==========================================================
    #  ЗАГРУЗКА
    # ==========================================================
    def load_orders(self):
        """Загружает заказы из БД."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            orders = om.get_all_orders()
            for order in orders:
                order_id = order[0]
                date = order[1]
                client = order[2]

                total = om.get_order_total(order_id)

                self.tree.insert("", tk.END,
                                 values=(order_id, date, client,
                                         f"{total:.2f}"))

        except Exception as e:
            messagebox.showerror("Ошибка",
                                 f"Не удалось загрузить заказы:\n{e}")

    # ==========================================================
    #  ВЫБОР ЗАКАЗА
    # ==========================================================
    def on_order_select(self, event=None):
        """Открывает окно состава выбранного заказа."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ")
            return

        item = self.tree.item(selected[0])
        order_id = item["values"][0]

        try:
            from order_items_window import OrderItemsWindow
            # Передаём пользователя — 4-й аргумент
            OrderItemsWindow(self.window, order_id, self.user)
        except Exception as e:
            messagebox.showerror("Ошибка",
                                 f"Не удалось открыть состав заказа:\n{e}")