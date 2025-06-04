from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.paginator import OrderPaginator

async def show_orders(callback: types.CallbackQuery):
    paginator = OrderPaginator(callback.from_user.id)
    await paginator.send_page(callback.message)

async def process_order_accept(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[-1])
    # Логика принятия заказа
