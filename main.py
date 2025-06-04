import asyncio
from aiogram import Bot, Dispatcher, types
from config import TOKEN
from handlers import start_handler, text_handler

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await start_handler(message)

@dp.message_handler()
async def handle_message(message: types.Message):
    await text_handler(message)

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())