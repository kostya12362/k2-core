from factories.clients import create_client
from factories.orders import create_order
from factories.products import create_product
from factories.warehouses import create_stock_item, create_warehouse
from httpx import AsyncClient
import pytest


pytestmark = pytest.mark.asyncio


async def test_create_order(client: AsyncClient):
    customer = await create_client(client)
    product = await create_product(client, price="1000.00")
    warehouse = await create_warehouse(client)

    await create_stock_item(
        client,
        warehouse_id=warehouse["id"],
        product_id=product["id"],
        quantity=10,
    )

    response = await client.post(
        "/api/v1/orders",
        json={
            "client_id": customer["id"],
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 2,
                }
            ],
        },
    )

    assert response.status_code == 200, response.json()

    body = response.json()

    assert body["data"]["client_id"] == customer["id"]
    assert body["data"]["status"] == "created"
    assert body["data"]["total_amount"] == 2000.0

    assert len(body["data"]["items"]) == 1

    item = body["data"]["items"][0]

    assert item["product_id"] == product["id"]
    assert item["quantity"] == 2
    assert item["unit_price"] == 1000.0
    assert item["total_price"] == 2000.0

    assert item["product"]["id"] == product["id"]
    assert item["product"]["name"] == product["name"]
    assert item["product"]["sku"] == product["sku"]
    assert item["product"]["price"] == product["price"]


async def test_create_order_reserves_stock(client: AsyncClient):
    customer = await create_client(client)
    product = await create_product(client)
    warehouse = await create_warehouse(client)

    await create_stock_item(
        client,
        warehouse_id=warehouse["id"],
        product_id=product["id"],
        quantity=10,
    )

    await create_order(
        client,
        client_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    response = await client.get(f"/api/v1/warehouses/{warehouse['id']}/stock")

    assert response.status_code == 200, response.json()

    body = response.json()

    assert len(body["data"]) == 1
    assert body["data"][0]["quantity"] == 10
    assert body["data"][0]["reserved_quantity"] == 3
    assert body["data"][0]["available_quantity"] == 7


async def test_create_order_without_client(client: AsyncClient):
    product = await create_product(client)
    warehouse = await create_warehouse(client)

    await create_stock_item(
        client,
        warehouse_id=warehouse["id"],
        product_id=product["id"],
        quantity=10,
    )

    response = await client.post(
        "/api/v1/orders",
        json={
            "client_id": 999,
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404


async def test_create_order_without_items(client: AsyncClient):
    customer = await create_client(client)

    response = await client.post(
        "/api/v1/orders",
        json={
            "client_id": customer["id"],
            "items": [],
        },
    )

    assert response.status_code == 422


async def test_create_order_without_product(client: AsyncClient):
    customer = await create_client(client)

    response = await client.post(
        "/api/v1/orders",
        json={
            "client_id": customer["id"],
            "items": [
                {
                    "product_id": 999,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 400


async def test_create_order_when_product_not_in_stock(client: AsyncClient):
    customer = await create_client(client)
    product = await create_product(client)

    response = await client.post(
        "/api/v1/orders",
        json={
            "client_id": customer["id"],
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 400


async def test_create_order_with_not_enough_stock(client: AsyncClient):
    customer = await create_client(client)
    product = await create_product(client)
    warehouse = await create_warehouse(client)

    await create_stock_item(
        client,
        warehouse_id=warehouse["id"],
        product_id=product["id"],
        quantity=2,
    )

    response = await client.post(
        "/api/v1/orders",
        json={
            "client_id": customer["id"],
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 5,
                }
            ],
        },
    )

    assert response.status_code == 400


async def test_create_order_uses_any_available_warehouse(client: AsyncClient):
    customer = await create_client(client)
    product = await create_product(client, price="1000.00")
    warehouse = await create_warehouse(client)

    await create_stock_item(
        client,
        warehouse_id=warehouse["id"],
        product_id=product["id"],
        quantity=5,
    )

    response = await client.post(
        "/api/v1/orders",
        json={
            "client_id": customer["id"],
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 2,
                }
            ],
        },
    )

    assert response.status_code == 200, response.json()

    body = response.json()

    assert body["data"]["client_id"] == customer["id"]
    assert body["data"]["total_amount"] == 2000.0
    assert body["data"]["items"][0]["product_id"] == product["id"]


async def test_list_orders_by_client(client: AsyncClient):
    customer = await create_client(client)
    product = await create_product(client, price="1000.00")
    warehouse = await create_warehouse(client)

    await create_stock_item(
        client,
        warehouse_id=warehouse["id"],
        product_id=product["id"],
        quantity=10,
    )

    await create_order(
        client,
        client_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    response = await client.get(f"/api/v1/orders/client/{customer['id']}")

    assert response.status_code == 200, response.json()

    body = response.json()

    assert len(body["data"]) == 1

    order = body["data"][0]

    assert order["client_id"] == customer["id"]
    assert order["status"] == "created"
    assert order["total_amount"] == 2000.0

    assert len(order["items"]) == 1

    item = order["items"][0]

    assert item["product_id"] == product["id"]
    assert item["quantity"] == 2
    assert item["unit_price"] == 1000.0
    assert item["total_price"] == 2000.0

    assert item["product"]["id"] == product["id"]
    assert item["product"]["name"] == product["name"]
    assert item["product"]["sku"] == product["sku"]
    assert item["product"]["price"] == product["price"]


async def test_get_order(client: AsyncClient):
    customer = await create_client(client)
    product = await create_product(client, price="1000.00")
    warehouse = await create_warehouse(client)

    await create_stock_item(
        client,
        warehouse_id=warehouse["id"],
        product_id=product["id"],
        quantity=10,
    )

    order = await create_order(
        client,
        client_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    response = await client.get(f"/api/v1/orders/{order['id']}")

    assert response.status_code == 200, response.json()

    body = response.json()

    assert body["data"]["id"] == order["id"]
    assert body["data"]["client_id"] == customer["id"]
    assert body["data"]["status"] == "created"
    assert body["data"]["total_amount"] == 2000.0

    assert len(body["data"]["items"]) == 1

    item = body["data"]["items"][0]

    assert item["product_id"] == product["id"]
    assert item["quantity"] == 2
    assert item["unit_price"] == 1000.0
    assert item["total_price"] == 2000.0

    assert item["product"]["id"] == product["id"]
    assert item["product"]["name"] == product["name"]
    assert item["product"]["sku"] == product["sku"]
    assert item["product"]["price"] == product["price"]


async def test_get_order_not_found(client: AsyncClient):
    response = await client.get("/api/v1/orders/999")

    assert response.status_code == 404


async def test_list_orders_by_client_empty(client: AsyncClient):
    customer = await create_client(client)

    response = await client.get(f"/api/v1/orders/client/{customer['id']}")

    assert response.status_code == 200, response.json()

    body = response.json()

    assert body["data"] == []