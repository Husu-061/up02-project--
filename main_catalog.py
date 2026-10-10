"""Главное окно с каталогом."""
import tkinter as tk
from tkinter import ttk, filedialog
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


class CatalogWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("1200x700")
        self.root.configure(bg=COLOR_MAIN_BG)

        self.set_icon()

        # Переменные состояния (А7 — сохраняются автоматически)
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Все категории")
        self.sort_var = tk.StringVar(value="Без сортировки")

        # Пагинация (А9)
        self.page_size = 5
        self.current_page = 0
        self.filtered_products = []   # текущий отфильтрованный список

        # Привязки
        self.search_var.trace_add("write", lambda *a: self.refresh_catalog())
        self.category_var.trace_add("write", lambda *a: self.refresh_catalog())
        self.sort_var.trace_add("write", lambda *a: self.refresh_catalog())

        self.build_ui()
        self.refresh_catalog()

    def set_icon(self):
        try:
            if os.name == "nt" and os.path.exists("resources/icon.ico"):
                self.root.iconbitmap("resources/icon.ico")
            elif os.path.exists("resources/logo.png"):
                img = Image.open("resources/logo.png")
                img.thumbnail((32, 32))
                icon_img = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, icon_img) # type: ignore
                self.root.icon = icon_img  # type: ignore
        except Exception as e:
            print(f"[DEBUG] Иконка: {e}")

    def load_logo_proportional(self, path, max_size=(60, 60)):
        try:
            if not os.path.exists(path):
                return None
            img = Image.open(path)
            img.thumbnail(max_size)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"[DEBUG] Логотип: {e}")
            return None


    def build_ui(self):
        header = tk.Frame(self.root, bg=COLOR_SECONDARY_BG, height=80)
        header.pack(fill="x")
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
        categories = ["Все категории"] + self.get_categories()
        ttk.Combobox(header, textvariable=self.category_var,
                     values=categories, state="readonly",
                     width=10).pack(side="left", padx=5)

        # Сортировка
        tk.Label(header, text="Сорт.:", bg=COLOR_SECONDARY_BG,
                 font=font(FONT_SIZE_NORMAL)).pack(side="left", padx=(5, 5))
        ttk.Combobox(header, textvariable=self.sort_var,
                     values=["Без сортировки", "Цена ↑", "Цена ↓", "Название А-Я"],
                     state="readonly", width=13).pack(side="left", padx=5)

        # Экспорт (А5)
        tk.Button(header, text="📥 CSV",
                  command=self.export_to_csv,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=8, pady=3,
                  cursor="hand2").pack(side="left", padx=3)

        # Кнопка темы
        tk.Button(header, text="🌙",
                  command=self.toggle_theme,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=8, pady=3,
                  cursor="hand2").pack(side="left", padx=3)

        # Счётчик товаров (А3)
        self.count_label = tk.Label(header, text="Товаров: 0",
                                     bg=COLOR_SECONDARY_BG,
                                     font=font(FONT_SIZE_NORMAL, bold=True))
        self.count_label.pack(side="right", padx=15)

        # ===== ОБЛАСТЬ ПРОКРУТКИ =====
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

        # ===== ПАНЕЛЬ ПАГИНАЦИИ (А9) =====
        pagination_frame = tk.Frame(self.root, bg=COLOR_SECONDARY_BG, height=40)
        pagination_frame.pack(fill="x", side="bottom")
        pagination_frame.pack_propagate(False)

        tk.Button(pagination_frame, text="◀ Назад",
                  command=self.prev_page,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=15, pady=3,
                  cursor="hand2").pack(side="left", padx=10, pady=5)

        self.page_label = tk.Label(pagination_frame, text="Страница 1",
                                    bg=COLOR_SECONDARY_BG,
                                    font=font(FONT_SIZE_NORMAL, bold=True))
        self.page_label.pack(side="left", expand=True)

        tk.Button(pagination_frame, text="Вперёд ▶",
                  command=self.next_page,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=15, pady=3,
                  cursor="hand2").pack(side="right", padx=10, pady=5)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

  
    def toggle_theme(self):
        current = self.root.cget("bg")
        new_bg = "#2E2E2E" if current == COLOR_MAIN_BG else COLOR_MAIN_BG
        self.root.configure(bg=new_bg)
        self.canvas.configure(bg=new_bg)
        self.catalog_frame.configure(bg=new_bg)
        self.refresh_catalog()


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

    def refresh_catalog(self):
        """Применяет фильтры и сортировку, сохраняя состояние (А7)."""
        products = self.get_all_products()

        # Фильтр по жанру
        category = self.category_var.get()
        if category and category != "Все категории":
            products = [p for p in products if p[1] == category]

        # Поиск по нескольким полям (А6)
        query = self.search_var.get()
        products = [p for p in products if matches_query(p, query)]

        # Сортировка (А7 — сохраняется через StringVar)
        order = self.sort_var.get()
        if order == "Цена ↑":
            products.sort(key=lambda p: p[5] or 0)
        elif order == "Цена ↓":
            products.sort(key=lambda p: p[5] or 0, reverse=True)
        elif order == "Название А-Я":
            products.sort(key=lambda p: p[3] or "")

        # Обновляем счётчик (А3)
        self.count_label.config(text=f"Товаров: {len(products)}")

        # Сохраняем и сбрасываем страницу на первую
        self.filtered_products = products
        self.current_page = 0
        self.render_page()

    def render_page(self):
        """Рисует текущую страницу каталога."""
        for widget in self.catalog_frame.winfo_children():
            widget.destroy()

        total = len(self.filtered_products)
        start = self.current_page * self.page_size
        end = start + self.page_size
        page_products = self.filtered_products[start:end]

        for i, p in enumerate(page_products):
            create_product_card(self.catalog_frame, p, index=i)

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

    def export_to_csv(self):
        """Экспортирует текущий каталог в CSV-файл."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="catalog_export.csv"
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "ID", "Жанр", "Исполнитель", "Название",
                    "Длительность (сек)", "Цена", "Количество", "Обложка"
                ])
                for p in self.filtered_products:
                    writer.writerow(p)
            print(f"✅ Экспортировано в {path}")
        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    CatalogWindow().run()