"""Обработчик ошибок для приложения."""
import tkinter as tk
from tkinter import messagebox


def safe_call(func, *args, **kwargs):
    """
    Безопасный вызов функции с обработкой исключений.

    :param func: функция для вызова
    :param args: позиционные аргументы
    :param kwargs: именованные аргументы
    :return: результат func() или None при ошибке
    """
    try:
        return func(*args, **kwargs)

    except FileNotFoundError as e:
        messagebox.showerror(
            "Файл не найден",
            f"Не удалось открыть файл:\n{e}"
        )
        return None

    except ConnectionError as e:
        messagebox.showerror(
            "Ошибка соединения",
            f"Не удалось подключиться к БД:\n{e}"
        )
        return None

    except ValueError as e:
        messagebox.showwarning(
            "Неверное значение",
            f"Проверьте введённые данные:\n{e}"
        )
        return None

    except Exception as e:
        messagebox.showerror(
            "Ошибка",
            f"Произошла ошибка:\n{type(e).__name__}: {e}"
        )
        return None


def validate_positive_int(value, field_name="Значение"):
    """
    Проверяет, что значение — положительное целое число.

    :param value: значение для проверки (строка или число)
    :param field_name: название поля (для сообщения)
    :return: (True, число) при успехе, (False, текст_ошибки) при ошибке

    Примеры:
        validate_positive_int("5", "Количество")   → (True, 5)
        validate_positive_int("0", "Количество")   → (False, "Количество должно быть больше нуля")
        validate_positive_int("-3", "Количество")  → (False, "Количество должно быть больше нуля")
        validate_positive_int("abc", "Количество") → (False, "Количество должно быть целым числом")
    """
    try:
        number = int(value)
    except (ValueError, TypeError):
        return (False, f"{field_name} должно быть целым числом")

    if number <= 0:
        return (False, f"{field_name} должно быть больше нуля")

    return (True, number)