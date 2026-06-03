from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import TypeAdapter

from api.core.dependencies import Pagination, get_repository
from api.core.schemas.pagination import PageMeta, ResponsePage
from api.core.schemas.response import Response
from api.v1.exceptions import ProductNotFound, ProductWithSKUAlreadyExist
from repositories.api.products import ProductApiRepository

from .schemas import ProductCreate, ProductID, ProductRead, ProductUpdate

router = APIRouter()

ProductRepository = Annotated[
    ProductApiRepository, Depends(get_repository(ProductApiRepository))
]


@router.get("")
async def list_products(
    pagination: Pagination,
    repo: ProductRepository,
) -> ResponsePage[ProductRead]:

    items, total = await repo.list_products(
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return ResponsePage[ProductRead](
        data=TypeAdapter(list[ProductRead]).validate_python(items),
        page=PageMeta(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
        ),
    )


@router.get("/{id}")
async def get_product(
    product_id: ProductID,
    repo: ProductRepository,
) -> Response[ProductRead]:
    product = await repo.get_product_read(product_id)
    if not product:
        raise ProductNotFound(product_id)
    return Response[ProductRead](data=ProductRead.model_validate(product))


@router.post("")
async def create_product(
    data: ProductCreate,
    repo: ProductRepository,
) -> Response[ProductRead]:
    exists = await repo.get_product_by_sku(data.sku)
    if exists:
        raise ProductWithSKUAlreadyExist(sku=data.sku)

    product = await repo.create_product_read(
        name=data.name,
        sku=data.sku,
        price=data.price,
    )

    return Response[ProductRead](data=ProductRead.model_validate(product))


@router.patch("/{id}")
async def update_product(
    product_id: ProductID,
    data: ProductUpdate,
    repo: ProductRepository,
) -> Response[ProductRead]:

    product = await repo.get_product(product_id)

    if not product:
        raise ProductNotFound(product_id)

    product = await repo.update_product_read(
        product_id=product_id,
        name=data.name,
        price=data.price,
    )

    return Response[ProductRead](data=ProductRead.model_validate(product))


@router.delete("/{id}")
async def delete_product(
    product_id: ProductID,
    repo: ProductRepository,
) -> dict:
    deleted = await repo.delete_product(product_id)
    if not deleted:
        raise ProductNotFound(product_id)

    return {"message": "Product deleted"}
