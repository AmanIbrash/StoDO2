from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_order_kb(order_id: int, total: int, current: int):
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("📝 Подробнее", callback_data=f"order_detail_{order_id}"),
        InlineKeyboardButton("✅ Взять заказ", callback_data=f"order_accept_{order_id}")
    )
    kb.row(
        InlineKeyboardButton("⬅️", callback_data=f"order_prev_{current}"),
        InlineKeyboardButton(f"{current}/{total}", callback_data=" "),
        InlineKeyboardButton("➡️", callback_data=f"order_next_{current}")
    )
    return kb