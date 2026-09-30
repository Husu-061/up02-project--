price_input = input("Введите цену: ")
discount_input = input("Введите скидку (%): ")

try:
    price = float(price_input)
    discount_percent = float(discount_input)

    discount_amount = price * (discount_percent / 100)

    final_price = price - discount_amount
    

    print(f"Цена со скидкой: {final_price:.2f} руб.")
    
except ValueError:

    print("Ошибка: введите корректные числовые значения.")