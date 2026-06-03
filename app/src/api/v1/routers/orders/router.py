from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import TypeAdapter

from api.core.dependencies import get_repository
from api.core.schemas.response import Response, ResponseMulti
from api.v1.exceptions import OrderNotFound
from repositories.api.orders import OrderApiRepository
from services.orders import OrderService

from .schemas import OrderCreate, OrderID, OrderRead

router = APIRouter()


OrderRepository = Annotated[
    OrderApiRepository, Depends(get_repository(OrderApiRepository))
]


@router.post("")
async def create_order(
    data: OrderCreate,
    repo: OrderRepository,
) -> Response[OrderRead]:
    service = OrderService(repo)
    order = await service.create_order(data)
    return Response[OrderRead](data=OrderRead.model_validate(order))


@router.get("/{id}")
async def get_order(
    order_id: OrderID,
    repo: OrderRepository,
) -> Response[OrderRead]:
    order = await repo.get_order(order_id)
    if not order:
        raise OrderNotFound(order_id)
    return Response[OrderRead](data=OrderRead.model_validate(order))


@router.get("/client/{client_id}")
async def list_orders_by_client(
    client_id: int,
    repo: OrderRepository,
) -> ResponseMulti[OrderRead]:
    orders = await repo.list_orders_by_client(client_id)
    return ResponseMulti[OrderRead](
        data=TypeAdapter(list[OrderRead]).validate_python(orders)
    )
