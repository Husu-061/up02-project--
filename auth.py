"""Авторизация пользователей."""
import tkinter as tk
from tkinter import messagebox

from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, font
)
from database import get_user_by_login


class AuthWindow:
    """Окно авторизации."""

    def __init__(self, root, on_success):
        """
        Инициализация окна.

        :param root: главное окно
        :param on_success: callback при успешной авторизации
        """
        self.root = root
        self.on_success = on_success
        self.current_user = None

        self.window = tk.Toplevel(root)
        self.window.title("Авторизация")
        self.window.geometry("450x350")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.window.transient(root)
        self.window.grab_set()   # модальное окно

        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

        self.build_ui()

    # ==========================================================
    #  ИНТЕРФЕЙС
    # ==========================================================
    def build_ui(self):
        """Строит интерфейс окна."""
        # ===== Шапка =====
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="ВХОД В СИСТЕМУ",
                 font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(pady=15)

        # ===== Форма =====
        form = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        form.pack(pady=30, padx=30, fill="x")

        tk.Label(form, text="Логин:",
                 font=font(FONT_SIZE_NORMAL),
                 bg=COLOR_MAIN_BG).pack(anchor="w")

        self.login_var = tk.StringVar()
        entry = tk.Entry(form, textvariable=self.login_var, width=30,
                         font=font(FONT_SIZE_NORMAL))
        entry.pack(pady=5, fill="x")
        entry.focus_set()   # фокус на поле сразу

        # Enter — тоже вход
        entry.bind("<Return>", lambda e: self.login())

        # ===== Кнопка =====
        tk.Button(form, text="Войти",
                  command=self.login,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  relief="flat", padx=20, pady=5,
                  cursor="hand2").pack(pady=15)

        # ===== Подсказка =====
        tk.Label(form,
                 text="Пример: client1, client2, manager1, admin1",
                 font=font(FONT_SIZE_NORMAL),
                 fg="gray", bg=COLOR_MAIN_BG).pack()

    # ==========================================================
    #  ОБРАБОТКА ВХОДА
    # ==========================================================
    def login(self):
        """Обработчик входа."""
        login = self.login_var.get().strip()

        if not login:
            messagebox.showwarning("Ошибка", "Введите логин")
            return

        user = get_user_by_login(login)

        if not user:
            messagebox.showerror(
                "Ошибка",
                f"Пользователь '{login}' не найден"
            )
            return

        # user = (id, логин, фио, роль)
        self.current_user = user

        messagebox.showinfo(
            "Успех",
            f"Добро пожаловать, {user[2]}!\n"
            f"Ваша роль: {user[3]}"
        )

        self.window.destroy()
        self.on_success(user)