from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Client
from repositories.api.pagination import paginate_scalars


class ClientApiRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_clients(
        self,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[Client], int]:
        stmt = select(Client).order_by(Client.id.desc())

        return await paginate_scalars(
            self.session,
            stmt,
            limit=limit,
            offset=offset,
        )

    async def get_client(self, client_id: int) -> Client | None:
        return await self.session.get(Client, client_id)

    async def get_client_with_relations(self, client_id: int) -> Client | None:
        result = await self.session.execute(select(Client).where(Client.id == client_id))

        return result.scalar_one_or_none()

    async def create_client(
        self,
        *,
        name: str,
        email: str,
    ) -> Client:
        client = Client(
            name=name,
            email=email,
        )

        self.session.add(client)
        await self.session.flush()

        return client
