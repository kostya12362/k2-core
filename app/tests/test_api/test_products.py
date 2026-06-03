from factories.products import create_product
from httpx import AsyncClient
import pytest

pytestmark = pytest.mark.asyncio


async def test_create_product(client: AsyncClient):
    response = await client.post(
        "/api/v1/products",
        json={
            "name": "IPhone 15",
            "sku": "IPHONE-15",
            "price": "1000.00",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["id"] == 1
    assert body["data"]["name"] == "IPhone 15"
    assert body["data"]["sku"] == "IPHONE-15"
    assert body["data"]["price"] == 1000.0


async def test_create_product_duplicate_sku(client: AsyncClient):
    await create_product(client)

    response = await client.post(
        "/api/v1/products",
        json={
            "name": "Another IPhone",
            "sku": "IPHONE-15",
            "price": "900.00",
        },
    )

    assert response.status_code == 400


async def test_list_products(client: AsyncClient):
    await create_product(
        client,
        name="Product 1",
        sku="PRODUCT-1",
        price="10.00",
    )
    await create_product(
        client,
        name="Product 2",
        sku="PRODUCT-2",
        price="20.00",
    )

    response = await client.get("/api/v1/products")

    assert response.status_code == 200

    body = response.json()

    assert len(body["data"]) == 2
    assert body["page"]["total"] == 2


async def test_get_product(client: AsyncClient):
    product = await create_product(client)

    response = await client.get(f"/api/v1/products/{product['id']}")

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["id"] == product["id"]
    assert body["data"]["sku"] == product["sku"]
    assert body["data"]["status"] == "unavailable"


async def test_update_product(client: AsyncClient):
    product = await create_product(client)

    response = await client.patch(
        f"/api/v1/products/{product['id']}",
        json={
            "name": "Updated Product",
            "price": 1500.00,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["id"] == product["id"]
    assert body["data"]["name"] == "Updated Product"
    assert body["data"]["price"] == 1500.0


async def test_delete_product(client: AsyncClient):
    product = await create_product(client)

    delete_response = await client.delete(f"/api/v1/products/{product['id']}")
    get_response = await client.get(f"/api/v1/products/{product['id']}")

    assert delete_response.status_code == 200
    assert get_response.status_code == 404
