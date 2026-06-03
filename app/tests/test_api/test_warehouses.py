from factories.products import create_product
from factories.warehouses import create_stock_item, create_warehouse
from httpx import AsyncClient
import pytest

pytestmark = pytest.mark.asyncio


async def test_create_warehouse(client: AsyncClient):
    response = await client.post(
        "/api/v1/warehouses",
        json={
            "name": "Main Warehouse",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["id"] == 1
    assert body["data"]["name"] == "Main Warehouse"


async def test_create_warehouse_duplicate_name(client: AsyncClient):
    await create_warehouse(client)

    response = await client.post(
        "/api/v1/warehouses",
        json={
            "name": "Main Warehouse",
        },
    )

    assert response.status_code == 400


async def test_list_warehouses(client: AsyncClient):
    await create_warehouse(client, name="Warehouse 1")
    await create_warehouse(client, name="Warehouse 2")

    response = await client.get("/api/v1/warehouses")

    assert response.status_code == 200

    body = response.json()

    assert len(body["data"]) == 2
    assert body["page"]["total"] == 2


async def test_create_stock_item(client: AsyncClient):
    product_before = await create_product(client)
    warehouse = await create_warehouse(client)

    response = await client.post(
        f"/api/v1/warehouses/{warehouse['id']}/stock",
        json={
            "product_id": product_before["id"],
            "quantity": 10,
        },
    )

    product_after_requests = await client.get(f"/api/v1/products/{product_before['id']}")
    product_after = product_after_requests.json()
    assert response.status_code == 200
    body = response.json()

    assert body["data"]["warehouse_id"] == warehouse["id"]
    assert body["data"]["product_id"] == product_before["id"]
    assert body["data"]["quantity"] == 10
    assert body["data"]["reserved_quantity"] == 0
    assert body["data"]["available_quantity"] == 10

    assert product_before["status"] == "unavailable"
    assert product_after["data"]["status"] == "available"

    assert product_after["data"]["id"] == product_before["id"]


async def test_create_stock_item_product_not_found(client: AsyncClient):
    warehouse = await create_warehouse(client)

    response = await client.post(
        f"/api/v1/warehouses/{warehouse['id']}/stock",
        json={
            "product_id": 999,
            "quantity": 10,
        },
    )

    assert response.status_code == 404


async def test_create_duplicate_stock_item(client: AsyncClient):
    product = await create_product(client)
    warehouse = await create_warehouse(client)

    await create_stock_item(
        client,
        warehouse_id=warehouse["id"],
        product_id=product["id"],
        quantity=10,
    )

    response = await client.post(
        f"/api/v1/warehouses/{warehouse['id']}/stock",
        json={
            "product_id": product["id"],
            "quantity": 10,
        },
    )

    assert response.status_code == 400


async def test_list_stock_items(client: AsyncClient):
    product = await create_product(client)
    warehouse = await create_warehouse(client)

    await create_stock_item(
        client,
        warehouse_id=warehouse["id"],
        product_id=product["id"],
        quantity=10,
    )

    response = await client.get(f"/api/v1/warehouses/{warehouse['id']}/stock")

    assert response.status_code == 200

    body = response.json()

    assert len(body["data"]) == 1
    assert body["data"][0]["product_id"] == product["id"]


async def test_update_stock_item(client: AsyncClient):
    product = await create_product(client)
    warehouse = await create_warehouse(client)

    stock_item = await create_stock_item(
        client,
        warehouse_id=warehouse["id"],
        product_id=product["id"],
        quantity=10,
    )

    response = await client.patch(
        f"/api/v1/warehouses/stock/{stock_item['id']}",
        json={
            "quantity": 20,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["id"] == stock_item["id"]
    assert body["data"]["quantity"] == 20
    assert body["data"]["available_quantity"] == 20
