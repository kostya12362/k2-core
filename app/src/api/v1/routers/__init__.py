from fastapi import APIRouter

from api.v1.routers.clients.router import router as clients_router
from api.v1.routers.orders.router import router as orders_router
from api.v1.routers.products.router import router as products_router
from api.v1.routers.warehouses.router import router as warehouses_router
from config import settings

router = APIRouter(prefix=settings.public_api.urls.prefix)

router.include_router(
    clients_router,
    prefix="/clients",
    tags=["Clients"],
)

router.include_router(
    products_router,
    prefix="/products",
    tags=["Products"],
)

router.include_router(
    warehouses_router,
    prefix="/warehouses",
    tags=["Warehouses"],
)

router.include_router(
    orders_router,
    prefix="/orders",
    tags=["Orders"],
)
