from decimal import Decimal

from api.v1.exceptions import (
    ClientDoesNotExist,
    NotEnoughProductInStock,
    OrderMustContainItems,
    ProductDoesNotExist,
)
from api.v1.routers.orders.schemas import OrderCreate
from models import Order, OrderItem
from repositories.api.orders import OrderApiRepository


class OrderService:
    def __init__(self, repo: OrderApiRepository) -> None:
        self.repo = repo

    async def create_order(self, data: OrderCreate) -> Order:
        client = await self.repo.get_client(data.client_id)

        if not client:
            raise ClientDoesNotExist(data.client_id)

        if not data.items:
            raise OrderMustContainItems()

        order_items: list[OrderItem] = []
        total_amount = Decimal("0.00")

        for item in data.items:
            product = await self.repo.get_product(item.product_id)

            if not product:
                raise ProductDoesNotExist(item.product_id)

            stock_item = await self.repo.get_available_stock_item_for_update(
                product_id=item.product_id,
                quantity=item.quantity,
            )

            if not stock_item:
                raise NotEnoughProductInStock(item.product_id)

            stock_item.reserved_quantity += item.quantity

            unit_price = product.price
            total_price = unit_price * item.quantity
            total_amount += total_price

            order_items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                )
            )

        order = Order(
            client_id=data.client_id,
            total_amount=total_amount,
            items=order_items,
        )

        return await self.repo.create_order(order)
