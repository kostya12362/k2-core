from typing import Annotated

from fastapi import Path
from pydantic import Field, computed_field

from api.core.schemas.base import PublicSchema
from api.v1.routers.products.schemas import ProductID

WarehouseID = Annotated[int, Path(..., ge=1, alias="id")]


class WarehouseCreate(PublicSchema):
    name: str = Field(min_length=1, max_length=128)


class WarehouseRead(WarehouseCreate):
    id: WarehouseID


class StockItemUpdate(PublicSchema):
    quantity: int = Field(ge=0)


class StockItemCreate(StockItemUpdate):
    product_id: ProductID


class StockItemRead(StockItemCreate):
    id: int
    warehouse_id: WarehouseID
    reserved_quantity: int

    @computed_field
    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity
