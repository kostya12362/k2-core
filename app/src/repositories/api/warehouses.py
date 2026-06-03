from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Product, StockItem, Warehouse
from repositories.api.pagination import paginate_scalars


class WarehouseApiRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_warehouses(
        self,
        limit: int,
        offset: int,
    ) -> tuple[list[Warehouse], int]:
        stmt = select(Warehouse).order_by(Warehouse.id.desc())

        return await paginate_scalars(
            self.session,
            stmt,
            limit=limit,
            offset=offset,
        )

    async def get_warehouse(self, warehouse_id: int) -> Warehouse | None:
        return await self.session.get(Warehouse, warehouse_id)

    async def get_warehouse_by_name(self, name: str) -> Warehouse | None:
        result = await self.session.execute(
            select(Warehouse).where(Warehouse.name == name)
        )

        return result.scalar_one_or_none()

    async def create_warehouse(self, name: str) -> Warehouse:
        warehouse = Warehouse(name=name)

        self.session.add(warehouse)
        await self.session.flush()

        return warehouse

    async def get_product(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_stock_item(
        self,
        warehouse_id: int,
        product_id: int,
    ) -> StockItem | None:
        result = await self.session.execute(
            select(StockItem).where(
                StockItem.warehouse_id == warehouse_id,
                StockItem.product_id == product_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_stock_item_by_id(self, stock_item_id: int) -> StockItem | None:
        return await self.session.get(StockItem, stock_item_id)

    async def list_stock_items(self, warehouse_id: int) -> list[StockItem]:
        result = await self.session.execute(
            select(StockItem)
            .where(StockItem.warehouse_id == warehouse_id)
            .order_by(StockItem.id.desc())
            .options(selectinload(StockItem.product))
        )

        return list(result.scalars().all())

    async def create_stock_item(
        self,
        warehouse_id: int,
        product_id: int,
        quantity: int,
    ) -> StockItem:
        stock_item = StockItem(
            warehouse_id=warehouse_id,
            product_id=product_id,
            quantity=quantity,
            reserved_quantity=0,
        )

        self.session.add(stock_item)
        await self.session.flush()

        return stock_item

    async def update_stock_item_quantity(
        self,
        stock_item: StockItem,
        quantity: int,
    ) -> StockItem:
        stock_item.quantity = quantity

        await self.session.flush()

        return stock_item
