"""Общие функции работы с БД (пользователи, авторизация)."""
import sqlite3
from config import DB_PATH


def get_connection():
    """Соединение с БД."""
    return sqlite3.connect(DB_PATH)


def get_user_by_login(login):
    """
    Ищет пользователя по логину.

    :param login: логин
    :return: (id, логин, фио, роль) или None
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT Пользователь.id,
               Пользователь.логин,
               Пользователь.фио,
               Роль.название
        FROM Пользователь
        JOIN Роль ON Пользователь.роль_id = Роль.id
        WHERE Пользователь.логин = ?
    """, (login,))
    row = cur.fetchone()
    conn.close()
    return row


def get_all_users():
    """Возвращает всех пользователей с ролями."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT Пользователь.id,
               Пользователь.логин,
               Пользователь.фио,
               Роль.название
        FROM Пользователь
        JOIN Роль ON Пользователь.роль_id = Роль.id
        ORDER BY Пользователь.id
    """)
    rows = cur.fetchall()
    conn.close()
    return rows