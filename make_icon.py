"""Создаёт icon.ico из logo.png."""
from PIL import Image

# Открываем logo.png и конвертируем в .ico
img = Image.open("resources/logo.png")
img.save("resources/icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
print("Иконка создана: resources/icon.ico")