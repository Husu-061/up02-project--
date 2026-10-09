"""Главное окно приложения с каталогом."""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sqlite3

from config import DB_PATH, APP_TITLE
from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE,
    font
)
from catalog import create_product_card


class CatalogWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("1200x700")
        self.root.configure(bg=COLOR_MAIN_BG)

        # Иконка приложения
        self.set_icon()

        # Переменные состояния (А1–А5 из пары 10)
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Все категории")
        self.sort_var = tk.StringVar(value="Без сортировки")

        self.search_var.trace_add("write", lambda *a: self.refresh_catalog())
        self.category_var.trace_add("write", lambda *a: self.refresh_catalog())
        self.sort_var.trace_add("write", lambda *a: self.refresh_catalog())

        self.build_ui()
        self.refresh_catalog()

    # ==========================================================
    #  ИКОНКА ПРИЛОЖЕНИЯ
    # ==========================================================
    def set_icon(self):
        """Устанавливает иконку приложения (кроссплатформенно)."""
        try:
            if os.name == "nt":   # Windows
                if os.path.exists("resources/icon.ico"):
                    self.root.iconbitmap("resources/icon.ico")
            else:                  # Linux / Mac
                if os.path.exists("resources/logo.png"):
                    img = Image.open("resources/logo.png")
                    img.thumbnail((32, 32))
                    icon_img = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, icon_img)
                    self.root.icon = icon_img  # type: ignore
        except Exception as e:
            print(f"[DEBUG] Иконка: {e}")

    # ==========================================================
    #  ЛОГОТИП С ПРОПОРЦИЯМИ
    # ==========================================================
    def load_logo_proportional(self, path, max_size=(60, 60)):
        """Загружает логотип с сохранением пропорций."""
        try:
            if not os.path.exists(path):
                return None
            img = Image.open(path)
            img.thumbnail(max_size)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"[DEBUG] Логотип: {e}")
            return None

    # ==========================================================
    #  ПОСТРОЕНИЕ ИНТЕРФЕЙСА
    # ==========================================================
    def build_ui(self):
        # ===== ШАПКА =====
        header = tk.Frame(self.root, bg=COLOR_SECONDARY_BG, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        # ===== Логотип (А2 — с возможностью смены) =====
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
                 bg=COLOR_SECONDARY_BG).pack(side="left", pady=15, padx=(0, 20))

        # ===== Поиск =====
        tk.Label(header, text="🔍", bg=COLOR_SECONDARY_BG,
                 font=font(FONT_SIZE_NORMAL)).pack(side="left")
        tk.Entry(header, textvariable=self.search_var, width=15,
                 font=font(FONT_SIZE_NORMAL)).pack(side="left", padx=5)

        # ===== Фильтр по жанру =====
        tk.Label(header, text="Жанр:", bg=COLOR_SECONDARY_BG,
                 font=font(FONT_SIZE_NORMAL)).pack(side="left", padx=(10, 5))
        categories = ["Все категории"] + self.get_categories()
        ttk.Combobox(header, textvariable=self.category_var,
                     values=categories, state="readonly",
                     width=12).pack(side="left", padx=5)

        # ===== Сортировка =====
        tk.Label(header, text="Сорт.:", bg=COLOR_SECONDARY_BG,
                 font=font(FONT_SIZE_NORMAL)).pack(side="left", padx=(10, 5))
        ttk.Combobox(header, textvariable=self.sort_var,
                     values=["Без сортировки", "Цена ↑", "Цена ↓", "Название А-Я"],
                     state="readonly", width=15).pack(side="left", padx=5)

        # ===== Кнопка смены логотипа (А2) =====
        tk.Button(header, text="🎨 Логотип",
                  command=self.change_logo,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=10, pady=3,
                  cursor="hand2").pack(side="left", padx=5)

        # ===== Кнопка тёмной темы (А5) =====
        tk.Button(header, text="🌙 Тема",
                  command=self.toggle_theme,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=10, pady=3,
                  cursor="hand2").pack(side="left", padx=5)

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

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ==========================================================
    #  СМЕНА ЛОГОТИПА (А2)
    # ==========================================================
    def change_logo(self):
        """Меняет логотип циклически между двумя файлами."""
        logos = ["resources/logo.png", "resources/logo_alt.png"]

        if not hasattr(self, "_current_logo_idx"):
            self._current_logo_idx = 0
        self._current_logo_idx = (self._current_logo_idx + 1) % len(logos)

        new_path = logos[self._current_logo_idx]
        new_logo = self.load_logo_proportional(new_path, max_size=(60, 60))
        if new_logo:
            self.logo_label.configure(image=new_logo)
            self.logo_label.image = new_logo  # type: ignore
            print(f"[DEBUG] Логотип сменён на: {new_path}")
        else:
            print(f"[DEBUG] Не удалось загрузить {new_path}")

    # ==========================================================
    #  ТЁМНАЯ ТЕМА (А5)
    # ==========================================================
    def toggle_theme(self):
        """Переключает светлую и тёмную тему."""
        current_bg = self.root.cget("bg")
        if current_bg == COLOR_MAIN_BG:
            new_bg = "#2E2E2E"
        else:
            new_bg = COLOR_MAIN_BG

        self.root.configure(bg=new_bg)
        self.canvas.configure(bg=new_bg)
        self.catalog_frame.configure(bg=new_bg)
        print(f"[DEBUG] Тема переключена: {new_bg}")

        # Перерисовываем карточки с новым фоном
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

    # ==========================================================
    #  ФИЛЬТРАЦИЯ + ПОИСК + СОРТИРОВКА
    # ==========================================================
    def refresh_catalog(self):
        for widget in self.catalog_frame.winfo_children():
            widget.destroy()

        products = self.get_all_products()

        # Фильтр по жанру
        category = self.category_var.get()
        if category and category != "Все категории":
            products = [p for p in products if p[1] == category]

        # Поиск
        query = self.search_var.get().lower().strip()
        if query:
            products = [
                p for p in products
                if query in (p[2] or "").lower() or query in (p[3] or "").lower()
            ]

        # Сортировка
        order = self.sort_var.get()
        if order == "Цена ↑":
            products.sort(key=lambda p: p[5])
        elif order == "Цена ↓":
            products.sort(key=lambda p: p[5], reverse=True)
        elif order == "Название А-Я":
            products.sort(key=lambda p: p[3] or "")

        # Отображаем карточки с чередованием фона (А3)
        for i, p in enumerate(products):
            create_product_card(self.catalog_frame, p, index=i)

        if not products:
            tk.Label(self.catalog_frame, text="Ничего не найдено",
                     font=font(FONT_SIZE_NORMAL),
                     bg=COLOR_MAIN_BG, fg="gray").pack(pady=50)

    def run(self):
        self.root.mainloop()


# ==========================================================
#  ПРОВЕРКА СООТВЕТСТВИЯ КИМ (А4)
# ==========================================================
def check_style_compliance():
    """Проверка соответствия КИМ (ресурсы, шрифт, цвета)."""
    report = []

    # 1. Ресурсы
    resources = [
        ("resources/picture.png", "Заглушка"),
        ("resources/logo.png", "Логотип"),
        ("resources/icon.ico", "Иконка"),
    ]
    for path, name in resources:
        if os.path.exists(path):
            report.append(f"✅ {name} ({path}) — есть")
        else:
            report.append(f"❌ {name} ({path}) — ОТСУТСТВУЕТ")

    # 2. Шрифт
    try:
        from styles import FONT_FAMILY
        if FONT_FAMILY == "Calibri":
            report.append(f"✅ Шрифт: {FONT_FAMILY} (по КИМ)")
        else:
            report.append(f"⚠️ Шрифт: {FONT_FAMILY} (ожидается Calibri)")
    except ImportError:
        report.append("❌ Модуль styles.py не найден")

    # 3. Цвета
    try:
        from styles import (COLOR_MAIN_BG, COLOR_SECONDARY_BG,
                            COLOR_ACCENT, COLOR_HIGHLIGHT)
        expected = {
            "COLOR_MAIN_BG": ("#FFFFFF", COLOR_MAIN_BG),
            "COLOR_SECONDARY_BG": ("#D2F6E7", COLOR_SECONDARY_BG),
            "COLOR_ACCENT": ("#70B2AF", COLOR_ACCENT),
            "COLOR_HIGHLIGHT": ("#ff8080", COLOR_HIGHLIGHT),
        }
        for name, (exp, got) in expected.items():
            if exp.upper() == got.upper():
                report.append(f"✅ {name}: {got}")
            else:
                report.append(f"❌ {name}: {got} (ожидается {exp})")
    except ImportError:
        report.append("❌ Не удалось импортировать цвета из styles.py")

    # 4. Папка images
    if os.path.exists("images"):
        count = len([f for f in os.listdir("images") if f.endswith(".png")])
        report.append(f"✅ Папка images/: {count} обложек")
    else:
        report.append("⚠️ Папка images/ не найдена")

    # Вывод
    print("=" * 50)
    print("ПРОВЕРКА СООТВЕТСТВИЯ КИМ")
    print("=" * 50)
    for line in report:
        print(line)
    print("=" * 50)


if __name__ == "__main__":
    check_style_compliance()
    CatalogWindow().run()
