from httpx import AsyncClient


async def create_product(
    client: AsyncClient,
    name: str = "IPhone 15",
    sku: str = "IPHONE-15",
    price: str = "1000.00",
) -> dict:
    response = await client.post(
        "/api/v1/products",
        json={
            "name": name,
            "sku": sku,
            "price": price,
        },
    )

    assert response.status_code == 200

    return response.json()["data"]
