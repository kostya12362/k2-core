from factories.clients import create_client
from httpx import AsyncClient
import pytest

pytestmark = pytest.mark.asyncio


async def test_create_client(client: AsyncClient):
    response = await client.post(
        "/api/v1/clients",
        json={
            "name": "Test Client",
            "email": "client@test.com",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["id"] == 1
    assert body["data"]["name"] == "Test Client"
    assert body["data"]["email"] == "client@test.com"


async def test_list_clients(client: AsyncClient):
    await create_client(
        client,
        name="Client 1",
        email="client1@test.com",
    )
    await create_client(
        client,
        name="Client 2",
        email="client2@test.com",
    )

    response = await client.get("/api/v1/clients")

    assert response.status_code == 200

    body = response.json()

    assert len(body["data"]) == 2
    assert body["page"]["total"] == 2


async def test_get_client(client: AsyncClient):
    created_client = await create_client(client)

    response = await client.get(f"/api/v1/clients/{created_client['id']}")

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["id"] == created_client["id"]
    assert body["data"]["email"] == created_client["email"]


async def test_get_client_not_found(client: AsyncClient):
    response = await client.get("/api/v1/clients/999")
    assert response.status_code == 404
