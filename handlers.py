from aiogram import types
from db import add_user
from keyboards import role_keyboard, main_menu

user_data = {}

async def start_handler(message: types.Message):
    await message.answer("Привет! Введи свой вуз:")
    user_data[message.from_user.id] = {}

async def text_handler(message: types.Message):
    uid = message.from_user.id
    step = user_data.get(uid, {})

    if "university" not in step:
        step["university"] = message.text
        await message.answer("Специальность?")
    elif "faculty" not in step:
        step["faculty"] = message.text
        await message.answer("ФИО?")
    elif "full_name" not in step:
        step["full_name"] = message.text
        await message.answer("Группа?")
    elif "group" not in step:
        step["group"] = message.text
        await message.answer("Выберите свою роль:", reply_markup=role_keyboard)
    elif "role" not in step:
        step["role"] = message.text
        add_user(
            telegram_id=uid,
            full_name=step["full_name"],
            university=step["university"],
            faculty=step["faculty"],
            group_name=step["group"],
            role=step["role"]
        )
        await message.answer("✅ Регистрация завершена! Добро пожаловать, {}.".format(step["full_name"]), reply_markup=main_menu)
        user_data.pop(uid, None)