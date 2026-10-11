"""Форма просмотра товара (музыкальный магазин)."""
import tkinter as tk
from tkinter import messagebox

from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_HEADER, FONT_SIZE_TITLE, font
)
from resources import get_product_image
from discount import calculate_price_with_discount
from utils import format_price
from error_handler import validate_positive_int, safe_call


class ViewForm:
    """Форма просмотра выбранного трека."""

    def __init__(self, parent, product, on_add_to_order=None):
        self.product = product
        self.on_add_to_order = on_add_to_order

        self.window = tk.Toplevel(parent)
        self.window.title(f"Просмотр — {product[3]}")
        self.window.geometry("800x650")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.window.transient(parent)

        # ЯВНО показываем окно
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

        # Закрытие по Esc
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        self.build_ui()

    # ==========================================================
    #  ПОСТРОЕНИЕ ИНТЕРФЕЙСА
    # ==========================================================
    def build_ui(self):
        """Строит интерфейс формы."""
        # ===== Шапка =====
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="КАРТОЧКА ТОВАРА",
                 font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(pady=15)

        # ===== Основная область =====
        main = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # ===== Изображение =====
        img_frame = tk.Frame(main, bg=COLOR_MAIN_BG)
        img_frame.pack(side="left", padx=10, anchor="n")

        cover = self.product[7]
        image_path = f"images/{cover}" if cover else None
        photo = safe_call(get_product_image, image_path, size=(200, 200))
        if photo:
            img_label = tk.Label(img_frame, image=photo, bg=COLOR_MAIN_BG)
            img_label.image = photo  # type: ignore
            img_label.pack()
        else:
            tk.Label(img_frame, text="📷\nНет фото",
                     font=font(FONT_SIZE_NORMAL),
                     bg=COLOR_MAIN_BG, fg="#888888",
                     width=20, height=10).pack()

        # ===== Информация =====
        info_frame = tk.Frame(main, bg=COLOR_MAIN_BG)
        info_frame.pack(side="left", fill="both", expand=True, padx=20)

        # Распаковка полей (по индексам — надёжно при любом количестве)
        product_id = self.product[0]
        genre      = self.product[1]
        artist     = self.product[2]
        title      = self.product[3]
        duration   = self.product[4]
        price      = self.product[5]
        qty        = self.product[6]
        cover      = self.product[7]

        # Описание — если есть 9-й элемент (Задание 1)
        description = None
        if len(self.product) > 8:
            description = self.product[8]

        # Проверки крайних случаев
        artist_safe   = artist if artist else "[Без исполнителя]"
        title_safe    = title  if title  else "[Без названия]"
        genre_safe    = genre  if genre  else "[Без жанра]"
        duration_safe = duration if duration is not None else 0
        price_safe    = price    if price    is not None else 0
        qty_safe      = qty      if qty      is not None else 0
        desc_safe     = description if description else "[Без описания]"

        # ===== Поля =====
        self._add_field(info_frame, "Исполнитель", artist_safe)
        self._add_field(info_frame, "Название",    title_safe)
        self._add_field(info_frame, "Жанр",        genre_safe)
        self._add_field(info_frame, "Длительность",
                        self._format_duration(duration_safe))
        self._add_field(info_frame, "Количество",
                        f"{qty_safe} шт. ({self._indicator(qty_safe)})")
        self._add_field(info_frame, "Описание", desc_safe)

        # Цена со скидкой
        final_price = safe_call(calculate_price_with_discount,
                                product_id, price_safe)
        if final_price is None:
            final_price = price_safe

        if final_price < price_safe:
            price_text = f"{format_price(final_price)} руб. (скидка!)"
        else:
            price_text = f"{format_price(price_safe)} руб."
        self._add_field(info_frame, "Цена", price_text, bold=True)

        # ===== Поле ввода количества (Задание 2) =====
        input_frame = tk.Frame(info_frame, bg=COLOR_MAIN_BG)
        input_frame.pack(fill="x", pady=(15, 5))

        tk.Label(input_frame, text="Кол-во для заказа:",
                 font=font(FONT_SIZE_NORMAL, bold=True),
                 bg=COLOR_MAIN_BG,
                 width=15, anchor="w").pack(side="left")

        self.qty_entry = tk.Entry(input_frame, width=10,
                                   font=font(FONT_SIZE_NORMAL))
        self.qty_entry.pack(side="left", padx=5)
        self.qty_entry.insert(0, "1")

        tk.Button(input_frame, text="Проверить",
                  command=self.check_quantity,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=10, pady=2,
                  cursor="hand2").pack(side="left", padx=5)

        # ===== Кнопки =====
        btn_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="✓ Добавить в заказ",
                  command=self.add_to_order,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=15, pady=5,
                  cursor="hand2").pack(side="left", padx=20)

        tk.Button(btn_frame, text="← Назад",
                  command=self.window.destroy,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=15, pady=5,
                  cursor="hand2").pack(side="right", padx=20)

    # ==========================================================
    #  ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ==========================================================
    def _add_field(self, parent, label, value, bold=False):
        """Добавляет поле «Метка: значение» в форму."""
        row = tk.Frame(parent, bg=COLOR_MAIN_BG)
        row.pack(fill="x", pady=4)

        tk.Label(row, text=f"{label}:",
                 font=font(FONT_SIZE_NORMAL, bold=True),
                 bg=COLOR_MAIN_BG,
                 width=15, anchor="w").pack(side="left")

        tk.Label(row, text=str(value),
                 font=font(FONT_SIZE_NORMAL, bold=bold),
                 bg=COLOR_MAIN_BG,
                 anchor="w", wraplength=350,
                 justify="left").pack(side="left", fill="x")

    def _format_duration(self, seconds):
        """Секунды → М:СС."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"

    def _indicator(self, qty):
        """Индикатор количества (3 уровня)."""
        if qty > 20:
            return "много"
        elif qty > 5:
            return "средне"
        else:
            return "мало"

    # ==========================================================
    #  ПРОВЕРКА КОЛИЧЕСТВА
    # ==========================================================
    def check_quantity(self):
        """Проверяет ввод количества через validate_positive_int."""
        value = self.qty_entry.get()
        ok, result = validate_positive_int(value, "Количество")

        if ok:
            messagebox.showinfo(
                "Проверка пройдена",
                f"Количество корректно: {result} шт."
            )
        else:
            messagebox.showwarning(
                "Ошибка ввода",
                str(result)     # ← str() для Pylance
            )

    # ==========================================================
    #  ДОБАВЛЕНИЕ В ЗАКАЗ
    # ==========================================================
    def add_to_order(self):
        """Обработчик кнопки «Добавить в заказ»."""
        # 1. Проверяем ввод количества
        value = self.qty_entry.get()
        ok, result = validate_positive_int(value, "Количество")

        if not ok:
            messagebox.showwarning("Ошибка ввода", str(result))   # ← str()
            return

        # 2. Проверка callback
        if not self.on_add_to_order:
            messagebox.showinfo(
                "Информация",
                "Функция в разработке"
            )
            return

        # 3. Проверка товара
        if not self.product:
            messagebox.showerror(
                "Ошибка",
                "Товар не выбран"
            )
            return

        # 4. Вызов callback
        try:
            self.on_add_to_order(self.product, result)
            messagebox.showinfo(
                "Успех",
                f"Добавлено {result} шт. товара «{self.product[3]}»"
            )
        except TypeError:
            # Если callback не принимает второй аргумент
            self.on_add_to_order(self.product)
            messagebox.showinfo("Успех", "Товар добавлен в заказ")
        except Exception as e:
            messagebox.showerror(
                "Ошибка заказа",
                f"Не удалось добавить товар:\n{e}"
            )