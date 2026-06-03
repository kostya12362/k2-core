from typing import Annotated

from fastapi import Path
from pydantic import Field

from api.core.schemas.base import PublicSchema
from models.enums import ProductStatus

ProductID = Annotated[int, Path(..., ge=1, alias="id")]


class ProductUpdate(PublicSchema):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    price: float | None = Field(default=None, gt=0)


class ProductCreate(ProductUpdate):
    sku: str = Field(min_length=1, max_length=64)


class ProductShortRead(ProductCreate):
    id: ProductID


class ProductRead(ProductShortRead):
    status: ProductStatus
