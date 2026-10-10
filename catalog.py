"""Каталог товаров (музыкальный магазин)."""
import tkinter as tk

from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_HIGHLIGHT,
    FONT_SIZE_NORMAL, FONT_SIZE_HEADER,
    font
)
from resources import get_product_image
from discount import calculate_price_with_discount


# ==========================================================
#  ОСНОВНАЯ ФУНКЦИЯ — только собирает карточку из блоков
# ==========================================================
def create_product_card(parent, product, index=0):
    """
    Создаёт карточку товара по макету.

    :param parent: родительский контейнер
    :param product: кортеж из БД
        (id, жанр, исполнитель, название, длительность, цена, количество, обложка)
    :param index: порядковый номер (для чередования фона)
    """
    # Распаковка полей
    product_id, genre, artist, title, duration, price, qty, cover = product

    # Защита от None в qty (крайний случай)
    qty_safe = qty if qty is not None else 0

    bg_color = _get_card_color(qty_safe, index)

    card = tk.Frame(parent, bg=bg_color, bd=1, relief="solid")
    card.pack(fill="x", padx=10, pady=(5, 0))

    # Собираем карточку из мелких блоков
    _add_image(card, cover, bg_color)
    _add_text_info(card, product_id, genre, artist, title, duration,
                   price, qty_safe, bg_color)

    # Линия-разделитель снизу
    _add_separator(parent)

    return card


# ==========================================================
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ — каждый блок отвечает за одно
# ==========================================================
def _get_card_color(qty, index):
    """
    Определяет цвет фона карточки.

    Приоритет:
    1. Подсветка #ff8080, если остаток ≤ 3.
    2. Чередование: чётные — белые, нечётные — светло-зелёные.
    """
    if qty <= 3:
        return COLOR_HIGHLIGHT
    return COLOR_MAIN_BG if index % 2 == 0 else COLOR_SECONDARY_BG


def _add_image(card, cover, bg_color):
    """Добавляет изображение товара (или улучшенную заглушку)."""
    img_frame = tk.Frame(card, bg=bg_color)
    img_frame.pack(side="left", padx=10, pady=10)

    # Формируем путь к обложке (крайний случай: cover=None)
    image_path = f"images/{cover}" if cover else None

    photo = get_product_image(image_path, size=(100, 100))
    if photo:
        img_label = tk.Label(img_frame, image=photo, bg=bg_color)
        img_label.image = photo  # type: ignore
        img_label.pack()
    else:
        # Fallback, если даже заглушка не сгенерировалась
        tk.Label(img_frame, text="📷\nНет фото", bg=bg_color, fg="#888888",
                 width=10, height=5, font=font(FONT_SIZE_NORMAL)).pack()


def _add_text_info(card, product_id, genre, artist, title, duration,
                   price, qty, bg_color):
    """Добавляет текстовую информацию о товаре с проверками крайних случаев."""
    text_frame = tk.Frame(card, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # ===== Проверки крайних случаев (Задание 5) =====
    artist_safe   = artist   if artist   else "[Без исполнителя]"
    title_safe    = title    if title    else "[Без названия]"
    genre_safe    = genre    if genre    else "[Без жанра]"
    duration_safe = duration if duration is not None else 0
    price_safe    = price    if price    is not None else 0

    # Исполнитель | Название — жирным
    _add_label(text_frame, f"{artist_safe} | {title_safe}",
               bg_color, bold=True, size=FONT_SIZE_HEADER)

    # Жанр
    _add_label(text_frame, f"Жанр: {genre_safe}", bg_color)

    # Количество + индикатор
    _add_label(text_frame, f"Количество: {_indicator(qty)} ({qty} шт.)",
               bg_color)

    # Длительность
    _add_label(text_frame, f"Длительность: {_format_duration(duration_safe)}",
               bg_color)

    # Цена со скидкой
    _add_price_label(text_frame, product_id, price_safe, bg_color)


def _add_label(parent, text, bg_color, bold=False,
               size=FONT_SIZE_NORMAL, align=tk.W):
    """Добавляет метку с текстом (универсальная функция)."""
    tk.Label(parent, text=text, font=font(size, bold=bold),
             bg=bg_color, anchor=align).pack(fill="x")  # type: ignore


def _add_price_label(parent, product_id, price, bg_color):
    """Добавляет цену с учётом скидки."""
    final_price = calculate_price_with_discount(product_id, price)

    if final_price < price:
        # Скидка применена — красным
        text = f"{final_price:.2f} руб. (скидка!)"
        color = "red"
    else:
        text = f"{price:.2f} руб."
        color = "black"

    tk.Label(parent, text=text, font=font(FONT_SIZE_HEADER, bold=True),
             fg=color, bg=bg_color, anchor=tk.E).pack(fill="x")  # type: ignore


def _add_separator(parent):
    """Линия-разделитель под карточкой."""
    separator = tk.Frame(parent, height=2, bg="#888888")
    separator.pack(fill="x", padx=10, pady=(0, 5))


def _indicator(qty):
    """
    Индикатор количества на складе.

    >20     → 🟢 много
    6–20    → 🟡 средне
    ≤5      → 🔴 мало
    """
    if qty > 20:
        return "🟢 много"
    elif qty > 5:
        return "🟡 средне"
    else:
        return "🔴 мало"


def _format_duration(seconds):
    """Преобразует секунды в формат М:СС."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"