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
