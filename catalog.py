"""Каталог товаров (музыкальный магазин)."""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

from config import DB_PATH, COLOR_HIGHLIGHT, FONT_FAMILY
from discount import calculate_price_with_discount


def create_product_card(parent, product):
    """
    Создаёт карточку товара по макету.

    :param parent: родительский контейнер
    :param product: кортеж из БД (id, жанр, исполнитель, название,
                    длительность, цена, количество, обложка)
    """
    # === Распаковка полей (индексы соответствуют вашей таблице Товар) ===
    product_id  = product[0]
    genre       = product[1]
    artist      = product[2]
    title       = product[3]
    duration    = product[4]
    price       = product[5]
    qty         = product[6]
    cover       = product[7]


    # Подсветка, если товара мало на складе (≤ 3)
    bg_color = "#ff8080" if qty <= 3 else "white"

    # Карточка — рамка со всех сторон
    card = tk.Frame(parent, bg=bg_color, bd=1, relief="solid")
    card.pack(fill="x", padx=10, pady=5)

    # Добавляем тонкую линию-разделитель под карточкой
    separator = tk.Frame(parent, height=1, bg="#CCCCCC")
    separator.pack(fill="x", padx=10, pady=(0, 5))

    # === Изображение (слева) ===
    img_frame = tk.Frame(card, bg=bg_color)
    img_frame.pack(side="left", padx=10, pady=10)

    if cover:
     image_path = f"images/{cover}"
    else:
     image_path = "resources/picture.png"

    if not os.path.exists(image_path):
      image_path = "resources/picture.png"

    try:
        img = Image.open(image_path).resize((100, 100))
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(img_frame, image=photo, bg=bg_color)
        img_label.image = photo   # type: ignore
        img_label.pack()
    except Exception:
        tk.Label(img_frame, text="[ФОТО]", bg=bg_color,
                 width=10, height=5).pack()

    # === Текстовая часть (справа) ===
    text_frame = tk.Frame(card, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # Исполнитель | Название
    header = f"{artist} | {title}"
    tk.Label(text_frame, text=header, font=(FONT_FAMILY, 14, "bold"),
             bg=bg_color, anchor="w").pack(fill="x")

    # Жанр
    tk.Label(text_frame, text=f"Жанр: {genre}",
             font=(FONT_FAMILY, 11), bg=bg_color, anchor="w").pack(fill="x")

    # Количество
    indicator = "🟢 много" if qty > 20 else ("🟡 средне" if qty > 5 else "🔴 мало")
    tk.Label(text_frame, text=f"Количество: {indicator} ({qty} шт.)",
             font=(FONT_FAMILY, 11), bg=bg_color, anchor="w").pack(fill="x")

    # Длительность (вместо "Состав" из методички)
    minutes = duration // 60
    seconds = duration % 60
    tk.Label(text_frame, text=f"Длительность: {minutes}:{seconds:02d}",
             font=(FONT_FAMILY, 11), bg=bg_color, anchor="w").pack(fill="x")

    # Цена со скидкой (используем нашу функцию из discount.py)
    final_price = calculate_price_with_discount(product_id, price)
    if final_price < price:
        price_text = f"{final_price:.2f} руб. (скидка!)"
        price_color = "red"
    else:
        price_text = f"{price:.2f} руб."
        price_color = "black"

    tk.Label(text_frame, text=price_text,
             font=(FONT_FAMILY, 14, "bold"),
             fg=price_color,
             bg=bg_color, anchor="e").pack(fill="x")

    return card