from aiogram import executor
from config.settings import settings
from handlers import start_handlers, order_handlers
from middlewares.user_middleware import UserMiddleware

# Инициализация бота
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot)

# Регистрация middleware
dp.middleware.setup(UserMiddleware())

# Регистрация хендлеров
start_handlers.register_handlers(dp)
order_handlers.register_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    
