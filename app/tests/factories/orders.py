from httpx import AsyncClient


async def create_order(
    client: AsyncClient,
    client_id: int,
    product_id: int,
    quantity: int = 1,
) -> dict:
    response = await client.post(
        "/api/v1/orders",
        json={
            "client_id": client_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            ],
        },
    )

    assert response.status_code == 200, response.json()

    return response.json()["data"]
