"""Модуль работы с ресурсами."""
import os
from PIL import Image, ImageDraw, ImageTk


# =========================================
# Пути к ресурсам
# =========================================
PATH_PICTURE = "resources/picture.png"
PATH_LOGO = "resources/logo.png"
PATH_ICON = "resources/icon.ico"

# =========================================
# Кэш изображений (Задание А1)
# =========================================
_image_cache = {}


def create_placeholder(size=(100, 100)):
    """Создаёт заглушку с контуром фотоаппарата (Задание 1)."""
    img = Image.new("RGB", size, "#E0E0E0")
    draw = ImageDraw.Draw(img)
    w, h = size

    # Корпус фотоаппарата
    draw.rectangle([w * 0.15, h * 0.35, w * 0.85, h * 0.75],
                   outline="#888888", width=2)
    # Объектив
    draw.ellipse([w * 0.4, h * 0.45, w * 0.6, h * 0.65],
                 outline="#888888", width=2)
    # Вспышка
    draw.rectangle([w * 0.2, h * 0.28, w * 0.35, h * 0.35],
                   outline="#888888", width=2)
    return img


def load_image(path, size=(100, 100)):
    """
    Загружает изображение с указанным размером.
    Использует кэш (Задание А1).
    """
    key = (path, size)
    if key in _image_cache:
        return _image_cache[key]

    try:
        if not os.path.exists(path):
            return None
        img = Image.open(path).resize(size)
        photo = ImageTk.PhotoImage(img)
        _image_cache[key] = photo
        return photo
    except Exception as e:
        print(f"Ошибка загрузки {path}: {e}")
        return None


def load_image_proportional(path, max_size=(100, 100)):
    """Загружает изображение с сохранением пропорций (для логотипа)."""
    try:
        if not os.path.exists(path):
            return None
        img = Image.open(path)
        img.thumbnail(max_size)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Ошибка загрузки {path}: {e}")
        return None


def get_product_image(image_path, size=(100, 100)):
    """
    Возвращает картинку товара или улучшенную заглушку.
    Если картинки нет — генерирует заглушку с фотоаппаратом.
    """
    if image_path and os.path.exists(image_path):
        photo = load_image(image_path, size)
        if photo:
            return photo

    # Генерируем заглушку с фотоаппаратом
    try:
        placeholder = create_placeholder(size)
        return ImageTk.PhotoImage(placeholder)
    except Exception as e:
        print(f"Ошибка создания заглушки: {e}")
        return None