import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Замени "YOUR_BOT_TOKEN" на токен от @BotFather
API_TOKEN = '7641233572:AAH6ncl_6JvsO-dqTVDtxLwV3xMrrFw3IiQ'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Подключение к SQLite
conn = sqlite3.connect('studo.db')
cursor = conn.cursor()

# Создание таблиц, если их нет
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER UNIQUE,
    name TEXT,
    university TEXT,
    specialty TEXT,
    group_name TEXT,
    year INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    description TEXT,
    price INTEGER,
    deadline TEXT,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users (tg_id)
)
''')
conn.commit()

# States для регистрации и создания заказа
class Registration(StatesGroup):
    name = State()
    university = State()
    specialty = State()
    group = State()
    year = State()

class CreateOrder(StatesGroup):
    title = State()
    description = State()
    price = State()
    deadline = State()

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT * FROM users WHERE tg_id = ?', (user_id,))
    user = cursor.fetchone()

    if user:
        await message.answer("👋 Привет! Ты уже зарегистрирован. Используй /new_order, чтобы создать заказ, или /orders, чтобы просмотреть заказы.")
    else:
        await Registration.name.set()
        await message.answer("👋 Привет! Давай зарегистрируем тебя.\nВведи своё **ФИО**:")

# Регистрация: ФИО
@dp.message_handler(state=Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await Registration.next()
    await message.answer("🎓 В каком **университете** ты учишься?")

# Регистрация: университет
@dp.message_handler(state=Registration.university)
async def process_university(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['university'] = message.text

    await Registration.next()
    await message.answer("📚 Какая у тебя **специальность**?")

# Регистрация: специальность
@dp.message_handler(state=Registration.specialty)
async def process_specialty(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['specialty'] = message.text

    await Registration.next()
    await message.answer("👥 В какой **группе** ты учишься?")

# Регистрация: группа
@dp.message_handler(state=Registration.group)
async def process_group(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['group'] = message.text

    await Registration.next()
    await message.answer("📆 На каком **курсе** ты учишься? (1, 2, 3, ...)")

# Регистрация: курс
@dp.message_handler(state=Registration.year)
async def process_year(message: types.Message, state: FSMContext):
    try:
        year = int(message.text)
    except ValueError:
        await message.answer("❌ Введи число (1, 2, 3, ...)")
        return

    async with state.proxy() as data:
        data['year'] = year
        cursor.execute('''
        INSERT INTO users (tg_id, name, university, specialty, group_name, year)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (message.from_user.id, data['name'], data['university'], data['specialty'], data['group'], data['year']))
        conn.commit()

    await state.finish()
    await message.answer("✅ Регистрация завершена! Теперь ты можешь создавать заказы (/new_order) или просматривать доступные (/orders).")

# Команда /new_order - создание заказа
@dp.message_handler(commands=['new_order'])
async def new_order(message: types.Message):
    await CreateOrder.title.set()
    await message.answer("🏗 Введи **название** заказа:")

# Создание заказа: название
@dp.message_handler(state=CreateOrder.title)
async def process_order_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text

    await CreateOrder.next()
    await message.answer("📝 Напиши **описание** заказа:")

# Создание заказа: описание
@dp.message_handler(state=CreateOrder.description)
async def process_order_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

    await CreateOrder.next()
    await message.answer("💰 Укажи **цену** (в рублях):")

# Создание заказа: цена
@dp.message_handler(state=CreateOrder.price)
async def process_order_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("❌ Введи число (например, 1000)")
        return

    async with state.proxy() as data:
        data['price'] = price

    await CreateOrder.next()
    await message.answer("⏳ Укажи **срок выполнения** (например, 'до 15 июня'):")

# Создание заказа: дедлайн
@dp.message_handler(state=CreateOrder.deadline)
async def process_order_deadline(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['deadline'] = message.text
        cursor.execute('''
        INSERT INTO orders (user_id, title, description, price, deadline)
        VALUES (?, ?, ?, ?, ?)
        ''', (message.from_user.id, data['title'], data['description'], data['price'], data['deadline']))
        conn.commit()

    await state.finish()
    await message.answer("✅ Заказ создан! Теперь другие студенты смогут его увидеть через /orders.")

# Команда /orders - просмотр заказов
@dp.message_handler(commands=['orders'])
async def show_orders(message: types.Message):
    cursor.execute('SELECT * FROM orders WHERE status = "active"')
    orders = cursor.fetchall()

    if not orders:
        await message.answer("😕 Пока нет активных заказов.")
        return

    for order in orders:
        order_id, user_id, title, description, price, deadline, status = order
        await message.answer(
            f"📌 **{title}**\n"
            f"📝 {description}\n"
            f"💰 Цена: {price} руб.\n"
            f"⏳ Срок: {deadline}\n"
            f"🆔 ID заказа: {order_id}\n\n"
            f"Чтобы взять заказ, напиши /take_order_{order_id}",
            parse_mode="Markdown"
        )

# Обработка принятия заказа
@dp.message_handler(lambda message: message.text.startswith('/take_order_'))
async def take_order(message: types.Message):
    try:
        order_id = int(message.text.split('_')[-1])
    except ValueError:
        await message.answer("❌ Неверный формат команды.")
        return

    cursor.execute('SELECT * FROM orders WHERE id = ? AND status = "active"', (order_id,))
    order = cursor.fetchone()

    if not order:
        await message.answer("❌ Заказ не найден или уже закрыт.")
        return

    cursor.execute('UPDATE orders SET status = "taken" WHERE id = ?', (order_id,))
    conn.commit()

    order_creator_id = order[1]
    await bot.send_message(
        order_creator_id,
        f"🎉 Твой заказ **{order[2]}** взял @{message.from_user.username}! Свяжись с ним для уточнения деталей.",
        parse_mode="Markdown"
    )

    await message.answer(f"✅ Ты взял заказ! Заказчик получил уведомление. Его контакт: @{order_creator_id}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
