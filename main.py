
import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Нет BOT_TOKEN в .env файле")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

users = {}
orders = []
taken_orders = {}

class Register(StatesGroup):
    waiting_for_info = State()

class Order(StatesGroup):
    waiting_for_description = State()

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer(
            "Привет! 👋\n\nПеред тем как начать пользоваться ботом, нужно пройти быструю регистрацию. "
            "Это поможет сделать сервис безопасным и удобным для всех.\n\n"
            "Пожалуйста, отправь в одном сообщении:\n\n"
            "🧑‍🎓 Имя и фамилию\n🏫 Место учёбы и специальность\n\n"
            "👤 Пример: Арстангалиев Аман, КАЗГАСА, Архитектура"
        )
        await Register.waiting_for_info.set()
    else:
        await message.answer("Ты уже зарегистрирован! Выбирай действие:\n📝 /neworder — создать заказ\n📋 /orders — посмотреть заказы")

@dp.message_handler(state=Register.waiting_for_info)
async def process_registration(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    users[user_id] = message.text
    await message.answer("Отлично, регистрация завершена ✅\n\nТеперь ты можешь:\n— 📝 Создавать заказы (/neworder)\n— 📋 Смотреть заказы (/orders)")
    await state.finish()

@dp.message_handler(commands=["neworder"])
async def new_order(message: types.Message):
    if message.from_user.id not in users:
        await message.answer("Сначала нужно зарегистрироваться. Напиши /start")
        return
    await message.answer("✍️ Введите описание заказа:")
    await Order.waiting_for_description.set()

@dp.message_handler(state=Order.waiting_for_description)
async def process_order(message: types.Message, state: FSMContext):
    orders.append({"user_id": message.from_user.id, "text": message.text})
    await message.answer("✅ Заказ создан и доступен для исполнителей.")
    await state.finish()

@dp.message_handler(commands=["orders"])
async def list_orders(message: types.Message):
    if not orders:
        await message.answer("Пока нет доступных заказов.")
        return
    text = "📋 Доступные заказы:\n"
    for i, order in enumerate(orders):
        if order["user_id"] != message.from_user.id:
            text += f"{i+1}. {order['text']}\nНапиши /take_{i} чтобы взять\n\n"
    await message.answer(text)

@dp.message_handler(lambda message: message.text.startswith("/take_"))
async def take_order(message: types.Message):
    try:
        index = int(message.text.split("_")[1])
        order = orders[index]
    except:
        await message.answer("❌ Ошибка: заказ не найден")
        return

    if message.from_user.id == order["user_id"]:
        await message.answer("❌ Нельзя взять свой собственный заказ.")
        return

    taken_orders[message.from_user.id] = order
    orders.pop(index)
    await message.answer("✅ Ты взял заказ. Заказчик будет уведомлён (чат пока в разработке).")
