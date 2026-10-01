"""Проверка класса Product."""
from models import Product

p = Product(
    product_id=1,
    genre="Джаз",  
    artist="Луи Армстронг",  
    title="What a Wonderful World",  
    duration=245.0,  
    price=90.0,  
    quantity=3,  
)

print(p.info())
print(f"Скидка 25%: {p.price_with_discount(25):.2f} руб.")