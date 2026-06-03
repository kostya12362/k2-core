from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Client, Order, OrderItem, Product, StockItem


class OrderApiRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_client(self, client_id: int) -> Client | None:
        return await self.session.get(Client, client_id)

    async def get_product(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_available_stock_item_for_update(
        self,
        product_id: int,
        quantity: int,
    ) -> StockItem | None:
        result = await self.session.execute(
            select(StockItem)
            .where(
                StockItem.product_id == product_id,
                StockItem.quantity - StockItem.reserved_quantity >= quantity,
            )
            .order_by(StockItem.id.asc())
            .with_for_update(skip_locked=True)
        )

        return result.scalar_one_or_none()

    async def create_order(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.flush()

        result = await self.session.execute(
            select(Order)
            .where(Order.id == order.id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
            )
        )

        return result.scalar_one()

    async def get_order(self, order_id: int) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
            )
        )

        return result.scalar_one_or_none()

    async def list_orders_by_client(self, client_id: int) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.client_id == client_id)
            .order_by(Order.id.desc())
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
            )
        )

        return list(result.scalars().all())
