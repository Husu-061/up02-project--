"""Каталог товаров (музыкальный магазин)."""
import tkinter as tk

from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_HIGHLIGHT,
    FONT_SIZE_NORMAL, FONT_SIZE_HEADER,
    font
)
from resources import get_product_image
from discount import calculate_price_with_discount


def create_product_card(parent, product, index=0):
    """
    Создаёт карточку товара.

    :param parent: родительский контейнер
    :param product: кортеж из БД
        (id, жанр, исполнитель, название, длительность, цена, количество, обложка)
    :param index: порядковый номер (для чередования фона — Задание А3)
    """
    # ===== Распаковка полей =====
    product_id = product[0]
    genre      = product[1]
    artist     = product[2]
    title      = product[3]
    duration   = product[4]
    price      = product[5]
    qty        = product[6]
    cover      = product[7]

    # ===== Выбор фона =====
    # Приоритет: подсветка ≤3 > чередование
    if qty <= 3:
        bg_color = COLOR_HIGHLIGHT
    else:
        # Чередование: чётные — белый, нечётные — светло-зелёный (А3)
        bg_color = COLOR_MAIN_BG if index % 2 == 0 else COLOR_SECONDARY_BG

    # ===== Карточка =====
    card = tk.Frame(parent, bg=bg_color, bd=1, relief="solid")
    card.pack(fill="x", padx=10, pady=(5, 0))

    # ===== Изображение (слева) =====
    img_frame = tk.Frame(card, bg=bg_color)
    img_frame.pack(side="left", padx=10, pady=10)

    if cover:
        image_path = f"images/{cover}"
    else:
        image_path = None

    photo = get_product_image(image_path, size=(100, 100))
    if photo:
        img_label = tk.Label(img_frame, image=photo, bg=bg_color)
        img_label.image = photo  # type: ignore
        img_label.pack()
    else:
        # Fallback, если даже заглушка не сгенерировалась
        tk.Label(img_frame, text="📷\nНет фото", bg=bg_color, fg="#888888",
                 width=10, height=5, font=font(FONT_SIZE_NORMAL)).pack()

    # ===== Текстовая часть (справа) =====
    text_frame = tk.Frame(card, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # Исполнитель | Название
    header_text = f"{artist} | {title}"
    tk.Label(text_frame, text=header_text,
             font=font(FONT_SIZE_HEADER, bold=True),
             bg=bg_color, anchor="w").pack(fill="x")

    # Жанр
    tk.Label(text_frame, text=f"Жанр: {genre}",
             font=font(FONT_SIZE_NORMAL),
             bg=bg_color, anchor="w").pack(fill="x")

    # Количество + индикатор
    if qty > 20:
        indicator = "🟢 много"
    elif qty > 5:
        indicator = "🟡 средне"
    else:
        indicator = "🔴 мало"
    tk.Label(text_frame, text=f"Количество: {indicator} ({qty} шт.)",
             font=font(FONT_SIZE_NORMAL),
             bg=bg_color, anchor="w").pack(fill="x")

    # Длительность
    minutes = duration // 60
    seconds = duration % 60
    tk.Label(text_frame, text=f"Длительность: {minutes}:{seconds:02d}",
             font=font(FONT_SIZE_NORMAL),
             bg=bg_color, anchor="w").pack(fill="x")

    # Цена со скидкой
    final_price = calculate_price_with_discount(product_id, price)
    if final_price < price:
        price_text = f"{final_price:.2f} руб. (скидка!)"
        price_color = "red"
    else:
        price_text = f"{price:.2f} руб."
        price_color = "black"

    tk.Label(text_frame, text=price_text,
             font=font(FONT_SIZE_HEADER, bold=True),
             fg=price_color, bg=bg_color, anchor="e").pack(fill="x")

    # ===== Линия-разделитель =====
    separator = tk.Frame(parent, height=2, bg="#888888")
    separator.pack(fill="x", padx=10, pady=(0, 5))

    return card