class OrderPaginator:
    def __init__(self, user_id):
        self.user_id = user_id
        self.current_page = 1

    async def send_page(self, message):
        orders = get_orders(page=self.current_page)
        if orders:
            await message.edit_text(
                f"Заказ #{orders[0].id}",
                reply_markup=get_order_kb(orders[0].id, total_pages, self.current_page)
            )