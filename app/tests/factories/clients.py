from httpx import AsyncClient


async def create_client(
    client: AsyncClient,
    name: str = "Test Client",
    email: str = "client@test.com",
) -> dict:
    response = await client.post(
        "/api/v1/clients",
        json={
            "name": name,
            "email": email,
        },
    )

    assert response.status_code == 200

    return response.json()["data"]
