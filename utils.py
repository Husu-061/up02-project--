"""Вспомогательные утилиты."""


def format_price(price):
    """
    Форматирует цену с разделителем тысяч (Задание А1).
    15000 → "15 000"
    1250000 → "1 250 000"
    """
    if price is None:
        return "0"
    return f"{price:,.0f}".replace(",", " ")


def matches_query(product, query):
    """
    Проверяет, содержит ли товар поисковый запрос (Задание А6).
    Ищет по: исполнителю, названию, жанру.
    """
    if not query:
        return True
    query = query.lower().strip()
    return (
        query in str(product[1] or "").lower() or   # жанр
        query in str(product[2] or "").lower() or   # исполнитель
        query in str(product[3] or "").lower()      # название
    )