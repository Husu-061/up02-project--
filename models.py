class Product:
    def __init__(self, product_id, genre, artist, title, duration, price, quantity):
        """
        Инициализация товара (музыкального трека).
        
        :param product_id: идентификатор
        :param genre: жанр
        :param artist: исполнитель
        :param title: название композиции
        :param duration: длительность в секундах или минутах
        :param price: цена за единицу
        :param quantity: количество на складе
        :param cover_url: ссылка на обложку
        """
        self.id = product_id
        self.genre = genre
        self.artist = artist

        self.title = title  

        self.duration = duration 

        self.price = price
        self.quantity = quantity
    def is_available(self) -> bool: 
     return self.quantity > 0

    def total(self) -> float:
        return self.price * self.quantity

    def price_with_discount(self, discount_percent: float) -> float:
        return self.price * (1 - discount_percent / 100)

    def indicator(self) -> str:
        if self.quantity > 20:
            return "🟢 много"
        elif self.quantity <= 5:
            return "🛑 мало!"
        else:
            return "🟡 средне"

    def info(self) -> str:
        return (
            f"{self.artist} — {self.title}"
            f" ({self.genre}) | Цена: {self.price:.2f} руб."
            f" | Кол-во на складе: {self.quantity} шт. "
            f"[{self.indicator()}]"
        )


class Order:
    """Класс Заказ."""

    def __init__(self, order_id, date, client, product_id, quantity):
        self.id = order_id
        self.date = date
        self.client = client
        self.product_id = product_id  # ЧИСЛОВОЙ id из БД
        self.quantity = quantity

    product: Product | None = None
    def total(self) -> float | None:
        if hasattr(self, "product") and isinstance(self.product, Product):
            return self.product.price * self.quantity
        
        return None


    def info(self) -> str:
        # Сначала проверяем наличие объекта товара.
        # Используем локальные переменные, чтобы избежать повторных проверок.
        product_obj = getattr(self, 'product', None)

        name = (
            f"{getattr(product_obj, 'title', '')} ({getattr(product_obj, 'artist', '')})"
            if product_obj else 
            f"❗Товар №{self.product_id}"
        )

        price_str = (
            f"{getattr(product_obj, 'price', '-'):.2f} ₽ × {self.quantity} шт."
            if product_obj else "-"
        )

        status = ""
        if not product_obj or product_obj.quantity <= 0:
            status = "🛑 НЕТ В НАЛИЧИИ"

        return (
            f"\nЗаказ №{self.id}:"
            f"\tДата: {self.date}\n"
            f"\tКлиент: {self.client}\n"
            f"\tТовар: {name}, Кол-во: {price_str}{status}\n"
            f"\tИтого: {self.total() or '-'}"
        )