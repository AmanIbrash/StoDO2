import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.filters import Command
from dotenv import load_dotenv
import os
import uuid

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# FSM: Состояния для регистрации
class Registration(StatesGroup):
    name = State()
    university = State()
    role = State()

# FSM: Состояния для заказа
class OrderCreation(StatesGroup):
    title = State()
    description = State()

# Временные базы
users = {}
orders = {}

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    if message.from_user.id not in users:
        await message.answer("Привет! Для начала работы пройди регистрацию.Напиши своё имя и фамилию:")
        await state.set_state(Registration.name)
    else:
        await message.answer("""
С возвращением! 
Выбери действие:
1. Разместить заказ
2. Посмотреть заказы
""")

@dp.message(Registration.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Теперь напиши место учебы и специальность (например: КАЗГАСА, Архитектура):")
    await state.set_state(Registration.university)

@dp.message(Registration.university)
async def reg_university(message: Message, state: FSMContext):
    await state.update_data(university=message.text)
    await message.answer("Ты хочешь быть заказчиком, исполнителем или обоими?
(Напиши: заказчик / исполнитель / оба)")
    await state.set_state(Registration.role)

@dp.message(Registration.role)
async def reg_role(message: Message, state: FSMContext):
    data = await state.get_data()
    role = message.text.lower()
    if role not in ["заказчик", "исполнитель", "оба"]:
        await message.answer("Пожалуйста, выбери: заказчик / исполнитель / оба")
        return
    users[message.from_user.id] = {
        "name": data["name"],
        "university": data["university"],
        "role": role
    }
    await state.clear()
    await message.answer("Регистрация завершена! Теперь ты можешь размещать заказы или брать их в работу.")

@dp.message(F.text.lower() == "разместить заказ")
async def create_order_start(message: Message, state: FSMContext):
    await message.answer("Введи заголовок заказа:")
    await state.set_state(OrderCreation.title)

@dp.message(OrderCreation.title)
async def order_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Теперь опиши задание подробнее:")
    await state.set_state(OrderCreation.description)

@dp.message(OrderCreation.description)
async def order_description(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = str(uuid.uuid4())
    orders[order_id] = {
        "title": data["title"],
        "description": message.text,
        "author": message.from_user.id,
        "executor": None
    }
    await state.clear()
    await message.answer("Заказ размещен!")

@dp.message(F.text.lower() == "посмотреть заказы")
async def show_orders(message: Message):
    available_orders = [o for o in orders.values() if o["executor"] is None and o["author"] != message.from_user.id]
    if not available_orders:
        await message.answer("Свободных заказов пока нет.")
        return
    for order in available_orders:
        await message.answer(f"<b>{order['title']}</b>
{order['description']}

Напиши 'взять {order['title']}' чтобы взять этот заказ")

@dp.message(F.text.lower().startswith("взять "))
async def take_order(message: Message):
    title = message.text[6:].strip().lower()
    for oid, order in orders.items():
        if order["title"].lower() == title and order["executor"] is None:
            order["executor"] = message.from_user.id
            await message.answer("Вы взяли заказ! Можете связаться с заказчиком через Telegram.")
            author_id = order["author"]
            await bot.send_message(author_id, f"Пользователь @{message.from_user.username} взял ваш заказ: {order['title']}")
            return
    await message.answer("Такого свободного заказа не найдено.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
