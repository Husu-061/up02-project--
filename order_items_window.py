"""Окно состава заказа (музыкальный магазин)."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, FONT_SIZE_HEADER, font
)
import order_manager as om


class OrderItemsWindow:
    """Окно состава заказа."""

    def __init__(self, parent, order_id, current_user=None):
        """
        :param parent: родительское окно
        :param order_id: id заказа
        :param current_user: (id, логин, фио, роль) — 4 элемента
        """
        self.order_id = order_id
        self.current_user = current_user

        self.window = tk.Toplevel(parent)
        self.window.title(f"Состав заказа №{order_id}")
        self.window.geometry("950x620")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.window.transient(parent)

        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        self.build_ui()
        self.load_order_info()
        self.load_items()

    # ==========================================================
    #  ПРОВЕРКА РОЛИ
    # ==========================================================
    def is_admin(self):
        """Администратор ли текущий пользователь?"""
        # У нас current_user = (id, логин, фио, роль) — роль в [3]
        return bool(self.current_user and self.current_user[3] == "Администратор")

    # ==========================================================
    #  ИНТЕРФЕЙС
    # ==========================================================
    def build_ui(self):
        # ===== Шапка =====
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text=f"СОСТАВ ЗАКАЗА №{self.order_id}",
                 font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(pady=15)

        # ===== Информация о заказе (дата, клиент) =====
        info_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        info_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(info_frame, text="Дата заказа:",
                 font=font(FONT_SIZE_NORMAL, bold=True),
                 bg=COLOR_MAIN_BG).pack(side="left", padx=5)

        self.date_var = tk.StringVar()
        # Администратор может редактировать — остальные readonly
        state = "normal" if self.is_admin() else "readonly"
        self.date_entry = tk.Entry(info_frame, textvariable=self.date_var,
                                   width=15, font=font(FONT_SIZE_NORMAL),
                                   state=state)
        self.date_entry.pack(side="left", padx=5)

        # Кнопка «Сохранить дату» — только для Администратора
        if self.is_admin():
            tk.Button(info_frame, text="💾 Сохранить дату",
                      command=self.save_date,
                      bg=COLOR_ACCENT, fg="white",
                      font=font(FONT_SIZE_NORMAL),
                      relief="flat", padx=10, pady=3,
                      cursor="hand2").pack(side="left", padx=10)

        tk.Label(info_frame, text="Клиент:",
                 font=font(FONT_SIZE_NORMAL, bold=True),
                 bg=COLOR_MAIN_BG).pack(side="left", padx=20)

        self.client_label = tk.Label(info_frame, text="",
                                     font=font(FONT_SIZE_NORMAL),
                                     bg=COLOR_MAIN_BG)
        self.client_label.pack(side="left")

        # ===== Таблица позиций =====
        # У вас: artist (исполнитель) вместо production, format вместо size
        columns = ("id", "name", "artist", "format",
                   "quantity", "price", "total")

        self.tree = ttk.Treeview(self.window, columns=columns,
                                 show="headings", height=12)

        self.tree.heading("id",       text="№")
        self.tree.heading("name",     text="Товар")
        self.tree.heading("artist",   text="Исполнитель")
        self.tree.heading("format",   text="Формат")
        self.tree.heading("quantity", text="Кол-во")
        self.tree.heading("price",    text="Цена")
        self.tree.heading("total",    text="Сумма")

        self.tree.column("id",       width=40,  anchor="center")
        self.tree.column("name",     width=180, anchor="w")
        self.tree.column("artist",   width=140, anchor="w")
        self.tree.column("format",   width=70,  anchor="center")
        self.tree.column("quantity", width=70,  anchor="center")
        self.tree.column("price",    width=90,  anchor="e")
        self.tree.column("total",    width=90,  anchor="e")

        scrollbar = ttk.Scrollbar(self.window, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 5))

        # ===== Итоговая сумма =====
        self.total_label = tk.Label(self.window, text="",
                                    font=font(FONT_SIZE_HEADER, bold=True),
                                    fg=COLOR_ACCENT,
                                    bg=COLOR_MAIN_BG)
        self.total_label.pack(pady=5)

        # ===== Кнопки =====
        btn_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        btn_frame.pack(fill="x", pady=10)

        # Кнопка «Удалить позицию» — только Администратор
        if self.is_admin():
            tk.Button(btn_frame, text="🗑 Удалить позицию",
                      command=self.delete_item,
                      bg="#ff8080", fg="white",
                      font=font(FONT_SIZE_NORMAL),
                      relief="flat", padx=15, pady=5,
                      cursor="hand2").pack(side="left", padx=20)

        tk.Button(btn_frame, text="🔄 Обновить",
                  command=self.refresh_all,
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
    #  ЗАГРУЗКА ДАННЫХ
    # ==========================================================
    def load_order_info(self):
        """Загружает дату и клиента заказа."""
        try:
            order = om.get_order_by_id(self.order_id)
            if order:
                self.date_var.set(order[1])
                self.client_label.config(text=order[2])
        except Exception as e:
            print(f"[DEBUG] Ошибка load_order_info: {e}")

    def load_items(self):
        """Загружает позиции заказа."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            items = om.get_order_items(self.order_id)

            if not items:
                self.total_label.config(text="ИТОГО: 0.00 руб.")
                return

            for item in items:
                item_id    = item[0]
                name       = item[1]   # название
                artist     = item[2]   # исполнитель
                format_    = item[3]   # формат
                quantity   = item[4]
                price      = item[5]
                item_total = quantity * price

                self.tree.insert("", tk.END,
                                 iid=str(item_id),
                                 values=(item_id, name, artist, format_,
                                         quantity,
                                         f"{price:.2f}",
                                         f"{item_total:.2f}"))

            total = om.get_order_total(self.order_id)
            self.total_label.config(text=f"ИТОГО: {total:.2f} руб.")

        except Exception as e:
            messagebox.showerror("Ошибка",
                                 f"Не удалось загрузить состав:\n{e}")

    # ==========================================================
    #  СОХРАНЕНИЕ ДАТЫ (только Администратор)
    # ==========================================================
    def save_date(self):
        """Сохраняет изменённую дату."""
        if not self.is_admin():
            messagebox.showerror("Доступ запрещён",
                                 "Только Администратор может менять дату")
            return

        new_date = self.date_var.get().strip()

        # Валидация формата
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Ошибка",
                "Неверный формат даты. Используйте ГГГГ-ММ-ДД\n"
                "Например: 2026-10-12"
            )
            return

        if om.update_order_date(self.order_id, new_date):
            messagebox.showinfo("Успех", f"Дата обновлена: {new_date}")
            self.refresh_all()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить дату")

    # ==========================================================
    #  УДАЛЕНИЕ ПОЗИЦИИ (только Администратор)
    # ==========================================================
    def delete_item(self):
        """Удаляет выбранную позицию."""
        if not self.is_admin():
            messagebox.showerror("Доступ запрещён",
                                 "Только Администратор может удалять позиции")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите позицию")
            return

        item = self.tree.item(selected[0])
        values = item["values"]
        item_id = values[0]
        item_name = values[1]
        item_qty = values[4]

        if not messagebox.askyesno(
            "Подтверждение",
            f"Удалить позицию «{item_name}» ({item_qty} шт.)?\n\n"
            f"Остаток товара будет восстановлен."
        ):
            return

        if om.delete_order_item(int(item_id)):
            messagebox.showinfo(
                "Успех",
                f"Позиция «{item_name}» удалена.\n"
                f"Остаток восстановлен на +{item_qty} шт."
            )
            self.refresh_all()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить позицию")

    # ==========================================================
    #  ОБНОВЛЕНИЕ
    # ==========================================================
    def refresh_all(self):
        """Обновляет информацию о заказе и позиции."""
        self.load_order_info()
        self.load_items()