"""Каталог товаров (музыкальный магазин)."""
import tkinter as tk

from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_HIGHLIGHT,
    FONT_SIZE_NORMAL, FONT_SIZE_HEADER,
    font
)
from resources import get_product_image
from discount import calculate_price_with_discount
from utils import format_price


class ToolTip:
    """Всплывающая подсказка при наведении на карточку."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, background="lightyellow",
                 relief="solid", borderwidth=1,
                 font=font(FONT_SIZE_NORMAL)).pack()

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


def create_product_card(parent, product, index=0):
    """Создаёт карточку товара по макету."""
    product_id, genre, artist, title, duration, price, qty, cover = product
    qty_safe = qty if qty is not None else 0
    bg_color = _get_card_color(qty_safe, index)

    card = tk.Frame(parent, bg=bg_color, bd=1, relief="solid")
    card.pack(fill="x", padx=10, pady=(5, 0))

    _add_image(card, cover, bg_color)
    _add_text_info(card, product_id, genre, artist, title, duration,
                   price, qty_safe, bg_color)

    _add_separator(parent)

    # Tooltip (А2) — полная информация при наведении
    tooltip_text = (
        f"Исполнитель: {artist or '[не указан]'}\n"
        f"Название: {title or '[не указано]'}\n"
        f"Жанр: {genre or '[не указан]'}\n"
        f"Длительность: {_format_duration(duration or 0)}\n"
        f"Остаток: {qty_safe} шт."
    )
    ToolTip(card, tooltip_text)

    return card

def _get_card_color(qty, index):
    if qty <= 3:
        return COLOR_HIGHLIGHT
    return COLOR_MAIN_BG if index % 2 == 0 else COLOR_SECONDARY_BG


def _add_image(card, cover, bg_color):
    img_frame = tk.Frame(card, bg=bg_color)
    img_frame.pack(side="left", padx=10, pady=10)

    image_path = f"images/{cover}" if cover else None
    photo = get_product_image(image_path, size=(100, 100))
    if photo:
        img_label = tk.Label(img_frame, image=photo, bg=bg_color)
        img_label.image = photo  # type: ignore
        img_label.pack()
    else:
        tk.Label(img_frame, text="📷\nНет фото", bg=bg_color, fg="#888888",
                 width=10, height=5, font=font(FONT_SIZE_NORMAL)).pack()


def _add_text_info(card, product_id, genre, artist, title, duration,
                   price, qty, bg_color):
    text_frame = tk.Frame(card, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    artist_safe   = artist if artist else "[Без исполнителя]"
    title_safe    = _truncate_title(title, max_length=60)
    genre_safe    = genre  if genre  else "[Без жанра]"
    duration_safe = duration if duration is not None else 0
    price_safe    = _safe_price(price)

    _add_label(text_frame, f"{artist_safe} | {title_safe}",
               bg_color, bold=True, size=FONT_SIZE_HEADER)
    _add_label(text_frame, f"Жанр: {genre_safe}", bg_color)
    _add_label(text_frame, f"Количество: {_indicator(qty)} ({qty} шт.)", bg_color)
    _add_label(text_frame, f"Длительность: {_format_duration(duration_safe)}", bg_color)
    _add_price_label(text_frame, product_id, price_safe, bg_color)


def _add_label(parent, text, bg_color, bold=False,
               size=FONT_SIZE_NORMAL, align=tk.W):
    tk.Label(parent, text=text, font=font(size, bold=bold),
             bg=bg_color, anchor=align).pack(fill="x")  # type: ignore


def _add_price_label(parent, product_id, price, bg_color):
    """Добавляет цену с учётом скидки и разделителями тысяч (А1)."""
    final_price = calculate_price_with_discount(product_id, price)
    price_str = format_price(final_price)

    if final_price < price:
        text = f"{price_str} руб. (скидка!)"
        color = "red"
    else:
        text = f"{price_str} руб."
        color = "black"

    tk.Label(parent, text=text, font=font(FONT_SIZE_HEADER, bold=True),
             fg=color, bg=bg_color, anchor=tk.E).pack(fill="x")  # type: ignore


def _add_separator(parent):
    separator = tk.Frame(parent, height=2, bg="#888888")
    separator.pack(fill="x", padx=10, pady=(0, 5))


def _indicator(qty):
    if qty > 20:
        return "🟢 много"
    elif qty > 5:
        return "🟡 средне"
    else:
        return "🔴 мало"


def _format_duration(seconds):
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def _safe_price(price):
    if price is None or price < 0:
        return 0
    return price


def _truncate_title(title, max_length=60):
    if not title:
        return "[Без названия]"
    if len(title) <= max_length:
        return title
    return title[:max_length - 1] + "…"