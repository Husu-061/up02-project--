"""Главное окно с каталогом."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import sqlite3
import csv

from config import DB_PATH, APP_TITLE
from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, FONT_SIZE_HEADER,
    font
)
from catalog import create_product_card
from utils import format_price, matches_query
from error_handler import safe_call
from logger import logger


class CatalogWindow:
    def __init__(self):
        logger.info("=" * 50)
        logger.info("Запуск приложения")

        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("1300x750")
        self.root.configure(bg=COLOR_MAIN_BG)

        # Центрируем окно на экране
        self.root.update_idletasks()
        w = 1300
        h = 750
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.set_icon()

        # ===== Пользователь (заполнится после авторизации) =====
        self.current_user = None   # (id, логин, фио, роль)

        # ===== Переменные — создаём сразу =====
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Все категории")
        self.sort_var = tk.StringVar(value="Без сортировки")

        # Пагинация
        self.page_size = 5
        self.current_page = 0
        self.filtered_products = []

        # ===== Пока окно пустое — показываем только авторизацию =====
        # Создаём заглушку, которую заменим после входа
        self.placeholder = tk.Label(
            self.root,
            text="⏳ Ожидание авторизации...",
            font=font(FONT_SIZE_TITLE),
            bg=COLOR_MAIN_BG, fg="gray"
        )
        self.placeholder.pack(expand=True)

        # Через 100 мс показываем окно авторизации
        self.root.after(100, self.show_auth_window)

    # ==========================================================
    #  ИКОНКА
    # ==========================================================
    def set_icon(self):
        try:
            if os.name == "nt":
                if os.path.exists("resources/icon.ico"):
                    self.root.iconbitmap("resources/icon.ico")
            else:
                if os.path.exists("resources/logo.png"):
                    img = Image.open("resources/logo.png")
                    img.thumbnail((32, 32))
                    icon_img = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, icon_img)  # type: ignore
                    self.root.icon = icon_img  # type: ignore
        except Exception as e:
            logger.warning(f"Иконка: {e}")

    def load_logo_proportional(self, path, max_size=(60, 60)):
        try:
            if not os.path.exists(path):
                return None
            img = Image.open(path)
            img.thumbnail(max_size)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            logger.error(f"Логотип: {e}")
            return None

    # ==========================================================
    #  ОКНО АВТОРИЗАЦИИ — открывается через after()
    # ==========================================================
    def show_auth_window(self):
        """Открывает окно авторизации поверх главного."""
        try:
            from auth import AuthWindow
            AuthWindow(self.root, self.on_login_success)
            logger.info("Окно авторизации открыто")
        except Exception as e:
            logger.critical(f"Ошибка открытия авторизации: {e}", exc_info=True)
            messagebox.showerror(
                "Ошибка",
                f"Не удалось открыть окно авторизации:\n{e}"
            )
            self.root.destroy()

    # ==========================================================
    #  ОБРАБОТЧИК УСПЕШНОГО ВХОДА
    # ==========================================================
    def on_login_success(self, user):
        """
        Обработчик успешной авторизации.

        :param user: (id, логин, фио, роль)
        """
        self.current_user = user
        logger.info(f"Авторизация: {user[1]} — {user[3]}")

        # Убираем заглушку
        self.placeholder.destroy()

        # Привязки переменных
        self.search_var.trace_add("write", lambda *a: self.refresh_catalog())
        self.category_var.trace_add("write", lambda *a: self.refresh_catalog())
        self.sort_var.trace_add("write", lambda *a: self.refresh_catalog())

        # Строим интерфейс и загружаем каталог
        self.build_ui()
        self.refresh_catalog()
        logger.info("Приложение готово")

    # ==========================================================
    #  ПОСТРОЕНИЕ ИНТЕРФЕЙСА
    # ==========================================================
    def build_ui(self):
        # ============ 1. ШАПКА ============
        header = tk.Frame(self.root, bg=COLOR_SECONDARY_BG, height=80)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Логотип
        logo = self.load_logo_proportional("resources/logo.png", max_size=(60, 60))
        if logo:
            self.logo_label = tk.Label(header, image=logo, bg=COLOR_SECONDARY_BG)
            self.logo_label.image = logo  # type: ignore
            self.logo_label.pack(side="left", padx=15)
        else:
            self.logo_label = tk.Label(header, text="[ЛОГОТИП]",
                                        bg=COLOR_SECONDARY_BG,
                                        font=font(FONT_SIZE_NORMAL))
            self.logo_label.pack(side="left", padx=15)

        # Заголовок
        tk.Label(header, text="КАТАЛОГ ТОВАРОВ",
                 font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(side="left", pady=15, padx=(0, 15))

        # Поиск
        tk.Label(header, text="🔍", bg=COLOR_SECONDARY_BG,
                 font=font(FONT_SIZE_NORMAL)).pack(side="left")
        tk.Entry(header, textvariable=self.search_var, width=12,
                 font=font(FONT_SIZE_NORMAL)).pack(side="left", padx=5)

        # Жанр
        tk.Label(header, text="Жанр:", bg=COLOR_SECONDARY_BG,
                 font=font(FONT_SIZE_NORMAL)).pack(side="left", padx=(5, 5))
        categories = ["Все категории"] + self.load_categories_safe()
        ttk.Combobox(header, textvariable=self.category_var,
                     values=categories, state="readonly",
                     width=10).pack(side="left", padx=5)

        # Сортировка
        tk.Label(header, text="Сорт.:", bg=COLOR_SECONDARY_BG,
                 font=font(FONT_SIZE_NORMAL)).pack(side="left", padx=(5, 5))
        ttk.Combobox(header, textvariable=self.sort_var,
                     values=["Без сортировки", "Цена ↑", "Цена ↓", "Название А-Я"],
                     state="readonly", width=13).pack(side="left", padx=5)

        # CSV
        tk.Button(header, text="📥 CSV",
                  command=self.export_to_csv,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=8, pady=3,
                  cursor="hand2").pack(side="left", padx=3)

        # Тема
        tk.Button(header, text="🌙",
                  command=self.toggle_theme,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=8, pady=3,
                  cursor="hand2").pack(side="left", padx=3)

        # ===== КНОПКА «ЗАКАЗЫ» — ТОЛЬКО МЕНЕДЖЕР / АДМИНИСТРАТОР =====
        if self.current_user and self.current_user[3] in ("Менеджер", "Администратор"):
            tk.Button(header, text="📋 Заказы",
                      command=self.open_orders,
                      bg=COLOR_ACCENT, fg="white",
                      font=font(FONT_SIZE_NORMAL),
                      relief="flat", padx=8, pady=3,
                      cursor="hand2").pack(side="left", padx=3)

        # Информация о пользователе — справа
        if self.current_user:
            user_info = f"👤 {self.current_user[2]} ({self.current_user[3]})"
            tk.Label(header, text=user_info,
                     bg=COLOR_SECONDARY_BG,
                     font=font(FONT_SIZE_NORMAL)).pack(side="right", padx=15)

        # Статистика
        self.count_label = tk.Label(header, text="Товаров: 0",
                                     bg=COLOR_SECONDARY_BG,
                                     font=font(FONT_SIZE_NORMAL, bold=True))
        self.count_label.pack(side="right", padx=15)

        self.stats_label = tk.Label(header, text="",
                                     bg=COLOR_SECONDARY_BG,
                                     font=font(FONT_SIZE_NORMAL, bold=True))
        self.stats_label.pack(side="right", padx=15)

        # ============ 2. ПАНЕЛЬ ПАГИНАЦИИ ============
        pagination_frame = tk.Frame(self.root, bg=COLOR_SECONDARY_BG, height=45)
        pagination_frame.pack(fill="x", side="bottom")
        pagination_frame.pack_propagate(False)

        tk.Button(pagination_frame, text="◀ Назад",
                  command=self.prev_page,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=20, pady=5,
                  cursor="hand2").pack(side="left", padx=15, pady=8)

        self.page_label = tk.Label(pagination_frame, text="Страница 1",
                                    bg=COLOR_SECONDARY_BG,
                                    font=font(FONT_SIZE_NORMAL, bold=True))
        self.page_label.pack(side="left", expand=True)

        tk.Button(pagination_frame, text="Вперёд ▶",
                  command=self.next_page,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=20, pady=5,
                  cursor="hand2").pack(side="right", padx=15, pady=8)

        # ============ 3. CANVAS ============
        self.canvas = tk.Canvas(self.root, bg=COLOR_MAIN_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical",
                                   command=self.canvas.yview)
        self.catalog_frame = tk.Frame(self.canvas, bg=COLOR_MAIN_BG)

        self.catalog_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.window_id = self.canvas.create_window(
            (0, 0), window=self.catalog_frame, anchor="nw"
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.window_id, width=e.width)
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ==========================================================
    #  ТЁМНАЯ ТЕМА
    # ==========================================================
    def toggle_theme(self):
        current = self.root.cget("bg")
        new_bg = "#2E2E2E" if current == COLOR_MAIN_BG else COLOR_MAIN_BG
        self.root.configure(bg=new_bg)
        self.canvas.configure(bg=new_bg)
        self.catalog_frame.configure(bg=new_bg)
        logger.info(f"Тема: {new_bg}")
        self.refresh_catalog()

    # ==========================================================
    #  РАБОТА С БД
    # ==========================================================
    def get_categories(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT жанр FROM Товар "
                    "WHERE жанр IS NOT NULL ORDER BY жанр")
        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows if r[0]]

    def get_all_products(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM Товар ORDER BY id")
        rows = cur.fetchall()
        conn.close()
        return rows

    def load_categories_safe(self):
        return safe_call(self.get_categories) or []

    # ==========================================================
    #  ЗАГРУЗКА КАТАЛОГА
    # ==========================================================
    def refresh_catalog(self):
        try:
            products = safe_call(self.get_all_products) or []

            category = self.category_var.get()
            if category and category != "Все категории":
                products = [p for p in products if p[1] == category]

            query = self.search_var.get()
            if query:
                products = [p for p in products if matches_query(p, query)]

            order = self.sort_var.get()
            if order == "Цена ↑":
                products.sort(key=lambda p: p[5] or 0)
            elif order == "Цена ↓":
                products.sort(key=lambda p: p[5] or 0, reverse=True)
            elif order == "Название А-Я":
                products.sort(key=lambda p: p[3] or "")

            self.count_label.config(text=f"Товаров: {len(products)}")

            many   = sum(1 for p in products if (p[6] or 0) > 20)
            middle = sum(1 for p in products if 5 < (p[6] or 0) <= 20)
            few    = sum(1 for p in products if (p[6] or 0) <= 5)
            self.stats_label.config(text=f"🟢 {many}   🟡 {middle}   🔴 {few}")

            self.filtered_products = products
            self.current_page = 0
            self.render_page()

        except Exception as e:
            logger.error(f"Ошибка каталога: {e}", exc_info=True)

    # ==========================================================
    #  ПАГИНАЦИЯ
    # ==========================================================
    def render_page(self):
        for widget in self.catalog_frame.winfo_children():
            widget.destroy()

        total = len(self.filtered_products)
        start = self.current_page * self.page_size
        end = start + self.page_size
        page_products = self.filtered_products[start:end]

        for i, p in enumerate(page_products):
            safe_call(create_product_card, self.catalog_frame, p,
                      index=i, refresh=self.refresh_catalog)

        total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        self.page_label.config(
            text=f"Страница {self.current_page + 1} из {total_pages} (всего: {total})"
        )

        if not page_products:
            tk.Label(self.catalog_frame, text="Ничего не найдено",
                     font=font(FONT_SIZE_NORMAL),
                     bg=COLOR_MAIN_BG, fg="gray").pack(pady=50)

    def next_page(self):
        if (self.current_page + 1) * self.page_size < len(self.filtered_products):
            self.current_page += 1
            self.render_page()
            self.canvas.yview_moveto(0)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page()
            self.canvas.yview_moveto(0)

    # ==========================================================
    #  ЭКСПОРТ
    # ==========================================================
    def export_to_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="catalog_export.csv"
        )
        if not path:
            logger.info("Экспорт отменён")
            return

        def _write_csv():
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "ID", "Жанр", "Исполнитель", "Название",
                    "Длительность (сек)", "Цена", "Количество", "Обложка", "Описание"
                ])
                for p in self.filtered_products:
                    writer.writerow(p)
            logger.info(f"Экспортировано {len(self.filtered_products)} в {path}")
            print(f"✅ Экспортировано в {path}")

        safe_call(_write_csv)

    # ==========================================================
    #  ОТКРЫТИЕ ОКНА ЗАКАЗОВ
    # ==========================================================
    def open_orders(self):
        """Открывает окно списка заказов (только Менеджер/Администратор)."""
        if not self.current_user or self.current_user[3] not in ("Менеджер", "Администратор"):
            messagebox.showerror(
                "Доступ запрещён",
                "У вас нет прав для просмотра заказов."
            )
            return

        try:
            from orders_window import OrdersWindow
            OrdersWindow(self.root)
            logger.info(f"Открыто окно заказов ({self.current_user[1]})")
        except Exception as e:
            logger.error(f"Ошибка открытия окна заказов: {e}", exc_info=True)

    # ==========================================================
    #  ЗАПУСК
    # ==========================================================
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        CatalogWindow().run()
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
        raise