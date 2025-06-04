from aiogram import types
from aiogram.dispatcher import FSMContext
from database.crud import get_user, create_user
from keyboards.main_menu import main_keyboard

async def cmd_start(message: types.Message, db: Session):
    user = get_user(db, message.from_user.id)
    if user:
        await message.answer("Главное меню:", reply_markup=main_keyboard())
    else:
        await message.answer("Добро пожаловать! Заполните профиль...")
        # Дальше логика регистрации