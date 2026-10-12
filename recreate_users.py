"""Пересоздание таблиц Роль и Пользователь (нормализация)."""
import sqlite3
from config import DB_PATH


def migrate_users():
    """Пересоздаёт таблицу Пользователь с роль_id и создаёт таблицу Роль."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Бэкап старых данных
    print("Шаг 1: Бэкап существующих пользователей...")
    cur.execute("DROP TABLE IF EXISTS Пользователь_backup")
    cur.execute("""
        CREATE TABLE Пользователь_backup AS
        SELECT id, логин, фио, роль FROM Пользователь
    """)
    rows = cur.execute("SELECT COUNT(*) FROM Пользователь_backup").fetchone()[0]
    print(f"  Сохранено записей: {rows}")

    # 2. Создаём таблицу Роль
    print("Шаг 2: Создаём таблицу Роль...")
    cur.execute("DROP TABLE IF EXISTS Роль")
    cur.execute("""
        CREATE TABLE Роль (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            название TEXT NOT NULL UNIQUE
        )
    """)
    cur.execute("INSERT INTO Роль (название) VALUES ('Клиент')")
    cur.execute("INSERT INTO Роль (название) VALUES ('Менеджер')")
    cur.execute("INSERT INTO Роль (название) VALUES ('Администратор')")

    # 3. Удаляем старую Пользователь
    print("Шаг 3: Удаляем старую таблицу Пользователь...")
    cur.execute("DROP TABLE Пользователь")

    # 4. Создаём новую Пользователь
    print("Шаг 4: Создаём новую таблицу Пользователь...")
    cur.execute("""
        CREATE TABLE Пользователь (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            логин TEXT NOT NULL UNIQUE,
            фио TEXT NOT NULL,
            роль_id INTEGER NOT NULL,
            FOREIGN KEY (роль_id) REFERENCES Роль(id)
        )
    """)

    # 5. Восстанавливаем данные (текстовую роль → роль_id)
    print("Шаг 5: Восстанавливаем данные...")
    cur.execute("SELECT id, логин, фио, роль FROM Пользователь_backup")
    old_users = cur.fetchall()

    for user_id, login, fio, role_name in old_users:
        # Ищем роль_id по названию
        cur.execute("SELECT id FROM Роль WHERE название = ?", (role_name,))
        row = cur.fetchone()
        role_id = row[0] if row else 1   # по умолчанию — Клиент

        cur.execute("""
            INSERT INTO Пользователь (id, логин, фио, роль_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, login, fio, role_id))

    # 6. Удаляем backup
    cur.execute("DROP TABLE Пользователь_backup")

    conn.commit()

    # Проверка
    print("\n=== Результат ===")
    cur.execute("SELECT id, название FROM Роль")
    for row in cur.fetchall():
        print(f"  Роль: {row[0]} — {row[1]}")

    cur.execute("""
        SELECT п.id, п.логин, п.фио, р.название
        FROM Пользователь п
        JOIN Роль р ON п.роль_id = р.id
    """)
    for row in cur.fetchall():
        print(f"  Пользователь: {row[0]}, {row[1]}, {row[2]}, {row[3]}")

    conn.close()
    print("\n✅ Миграция завершена!")


if __name__ == "__main__":
    migrate_users()