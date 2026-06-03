from typing import Annotated

from fastapi import Path
from pydantic import Field

from api.core.schemas.base import PublicSchema
from api.v1.routers.products.schemas import ProductShortRead

OrderID = Annotated[int, Path(..., ge=1, alias="id")]


class OrderItemCreate(PublicSchema):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1)


class OrderCreate(PublicSchema):
    client_id: int = Field(ge=1)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemRead(PublicSchema):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    product: ProductShortRead


class OrderRead(PublicSchema):
    id: int
    client_id: int
    status: str
    total_amount: float
    items: list[OrderItemRead]
