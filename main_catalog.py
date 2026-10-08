"""Главное окно приложения с каталогом."""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk 
import sqlite3

from config import DB_PATH, FONT_FAMILY
from catalog import create_product_card


APP_TITLE = "Музыкальный магазин — Каталог"


class CatalogWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("900x700")

        self.build_ui()
        self.load_products()

    def build_ui(self):
        # Заголовок
        header = tk.Frame(self.root, bg="#D2F6E7")
        header.pack(fill="x")


        try:
            logo = Image.open("resources/logo.png").resize((50, 50))
            logo_photo = ImageTk.PhotoImage(logo)
            logo_label = tk.Label(header, image=logo_photo, bg="#D2F6E7")
            logo_label.image = logo_photo  # type: ignore
            logo_label.pack(side="left", padx=10, pady=10)
        except Exception as e:
            print(f"[DEBUG] Логотип не найден: {e}")


        tk.Label(header, text="КАТАЛОГ ТОВАРОВ",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg="#D2F6E7").pack(pady=15)

        # Область с прокруткой
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical",
                                   command=self.canvas.yview)
        self.catalog_frame = tk.Frame(self.canvas, bg="white")
        self.catalog_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.catalog_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Прокрутка колёсиком мыши
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Прокрутка каталога колёсиком мыши."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_products(self):
        """Загружает товары из БД и создаёт карточки."""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM Товар ORDER BY id")
        products = cur.fetchall()
        conn.close()

        for p in products:
            create_product_card(self.catalog_frame, p)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    CatalogWindow().run()