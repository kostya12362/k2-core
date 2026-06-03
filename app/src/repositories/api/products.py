from decimal import Decimal

from sqlalchemy import case, delete, exists, func, literal, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.selectable import Select

from models import Product, StockItem
from models.enums import ProductStatus


class ProductApiRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @classmethod
    def _product_status_expr(cls) -> ColumnElement[str]:
        available_exists = exists().where(
            StockItem.product_id == Product.id,
            StockItem.quantity - StockItem.reserved_quantity > 0,
        )

        return case(
            (
                available_exists,
                literal(ProductStatus.available.value),
            ),
            else_=literal(ProductStatus.unavailable.value),
        ).label("status")

    @classmethod
    def _product_with_status_stmt(cls) -> Select[tuple[int, str, str, float, str]]:
        return select(
            Product.id.label("id"),
            Product.name.label("name"),
            Product.sku.label("sku"),
            Product.price.label("price"),
            cls._product_status_expr(),
        )

    @staticmethod
    def _product_to_read_dict(
        product: Product,
        status: ProductStatus,
    ) -> dict:
        return {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": float(product.price),
            "status": status.value,
        }

    async def list_products(
        self,
        limit: int,
        offset: int,
    ) -> tuple[list[dict], int]:
        stmt = (
            self._product_with_status_stmt()
            .order_by(Product.id.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        items = [dict(item) for item in result.mappings().all()]

        total_result = await self.session.execute(
            select(func.count()).select_from(Product)
        )
        total = total_result.scalar_one()

        return items, total

    async def get_product_read(self, product_id: int) -> dict | None:
        stmt = self._product_with_status_stmt().where(Product.id == product_id)

        result = await self.session.execute(stmt)
        item = result.mappings().one_or_none()

        if item is None:
            return None

        return dict(item)

    async def get_product(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_product_by_sku(self, sku: str) -> Product | None:
        result = await self.session.execute(select(Product).where(Product.sku == sku))

        return result.scalar_one_or_none()

    async def create_product_read(
        self,
        name: str,
        sku: str,
        price: float,
    ) -> dict:
        product = Product(
            name=name,
            sku=sku,
            price=Decimal(str(price)),
        )

        self.session.add(product)
        await self.session.flush()

        return self._product_to_read_dict(
            product,
            status=ProductStatus.unavailable,
        )

    async def update_product_read(
        self,
        product_id: int,
        name: str | None = None,
        price: float | None = None,
    ) -> dict | None:
        values = {}

        if name is not None:
            values["name"] = name

        if price is not None:
            values["price"] = Decimal(str(price))

        if not values:
            return await self.get_product_read(product_id)

        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(**values)
            .returning(
                Product.id.label("id"),
                Product.name.label("name"),
                Product.sku.label("sku"),
                Product.price.label("price"),
                self._product_status_expr(),
            )
        )

        result = await self.session.execute(stmt)
        item = result.mappings().one_or_none()

        if item is None:
            return None

        return dict(item)

    async def delete_product(self, product_id: int) -> bool:
        stmt = delete(Product).where(Product.id == product_id).returning(Product.id)

        result = await self.session.execute(stmt)
        deleted_id = result.scalar_one_or_none()

        await self.session.flush()

        return deleted_id is not None
