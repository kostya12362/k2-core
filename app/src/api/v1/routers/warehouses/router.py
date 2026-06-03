from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import TypeAdapter

from api.core.dependencies import Pagination, get_repository
from api.core.schemas.pagination import PageMeta, ResponsePage
from api.core.schemas.response import Response, ResponseMulti
from api.v1.exceptions import (
    ProductNotFound,
    QuantityCannotBeLess,
    StockItemAlreadyExists,
    StockItemNotFound,
    WarehouseAlreadyExists,
    WarehouseNotFound,
)
from repositories.api.warehouses import WarehouseApiRepository

from .schemas import (
    StockItemCreate,
    StockItemRead,
    StockItemUpdate,
    WarehouseCreate,
    WarehouseID,
    WarehouseRead,
)

router = APIRouter()

WarehouseRepository = Annotated[
    WarehouseApiRepository, Depends(get_repository(WarehouseApiRepository))
]


@router.get("")
async def list_warehouses(
    pagination: Pagination,
    repo: WarehouseRepository,
) -> ResponsePage[WarehouseRead]:

    items, total = await repo.list_warehouses(
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return ResponsePage[WarehouseRead](
        data=TypeAdapter(list[WarehouseRead]).validate_python(items),
        page=PageMeta(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
        ),
    )


@router.get("/{id}")
async def get_warehouse(
    warehouse_id: WarehouseID,
    repo: WarehouseRepository,
) -> Response[WarehouseRead]:

    warehouse = await repo.get_warehouse(warehouse_id)

    if not warehouse:
        raise WarehouseNotFound

    return Response[WarehouseRead](data=WarehouseRead.model_validate(warehouse))


@router.post("")
async def create_warehouse(
    data: WarehouseCreate,
    repo: WarehouseRepository,
) -> Response[WarehouseRead]:

    exists = await repo.get_warehouse_by_name(data.name)

    if exists:
        raise WarehouseAlreadyExists

    warehouse = await repo.create_warehouse(name=data.name)

    return Response[WarehouseRead](data=WarehouseRead.model_validate(warehouse))


@router.get("/{id}/stock")
async def list_stock_items(
    warehouse_id: WarehouseID,
    repo: WarehouseRepository,
) -> ResponseMulti[StockItemRead]:

    warehouse = await repo.get_warehouse(warehouse_id)

    if not warehouse:
        raise WarehouseNotFound

    items = await repo.list_stock_items(warehouse_id=warehouse_id)

    return ResponseMulti[StockItemRead](
        data=TypeAdapter(list[StockItemRead]).validate_python(items)
    )


@router.post("/{id}/stock")
async def create_stock_item(
    warehouse_id: WarehouseID,
    data: StockItemCreate,
    repo: WarehouseRepository,
) -> Response[StockItemRead]:
    warehouse = await repo.get_warehouse(warehouse_id)

    if not warehouse:
        raise WarehouseNotFound

    product = await repo.get_product(data.product_id)

    if not product:
        raise ProductNotFound(data.product_id)

    exists = await repo.get_stock_item(
        warehouse_id=warehouse_id,
        product_id=data.product_id,
    )

    if exists:
        raise StockItemAlreadyExists

    stock_item = await repo.create_stock_item(
        warehouse_id=warehouse_id,
        product_id=data.product_id,
        quantity=data.quantity,
    )

    return Response[StockItemRead](data=StockItemRead.model_validate(stock_item))


@router.patch("/stock/{stock_item_id}")
async def update_stock_item(
    stock_item_id: int,
    data: StockItemUpdate,
    repo: WarehouseRepository,
) -> Response[StockItemRead]:

    stock_item = await repo.get_stock_item_by_id(stock_item_id)

    if not stock_item:
        raise StockItemNotFound

    if data.quantity < stock_item.reserved_quantity:
        raise QuantityCannotBeLess

    stock_item = await repo.update_stock_item_quantity(
        stock_item,
        quantity=data.quantity,
    )

    return Response[StockItemRead](data=StockItemRead.model_validate(stock_item))
