from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

role_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
role_keyboard.add(KeyboardButton("Заказчик"), KeyboardButton("Исполнитель"), KeyboardButton("Оба"))

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("📝 Создать заказ"),
    KeyboardButton("📋 Все заказы")
).add(KeyboardButton("🙋‍♂️ Мои заказы"))