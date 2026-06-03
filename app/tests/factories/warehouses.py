from httpx import AsyncClient


async def create_warehouse(
    client: AsyncClient,
    name: str = "Main Warehouse",
) -> dict:
    response = await client.post(
        "/api/v1/warehouses",
        json={
            "name": name,
        },
    )

    assert response.status_code == 200

    return response.json()["data"]


async def create_stock_item(
    client: AsyncClient,
    warehouse_id: int,
    product_id: int,
    quantity: int = 10,
) -> dict:
    response = await client.post(
        f"/api/v1/warehouses/{warehouse_id}/stock",
        json={
            "product_id": product_id,
            "quantity": quantity,
        },
    )

    assert response.status_code == 200

    return response.json()["data"]
