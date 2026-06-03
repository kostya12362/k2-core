from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import TypeAdapter

from api.core.dependencies import Pagination, get_repository
from api.core.schemas.pagination import PageMeta, ResponsePage
from api.core.schemas.response import Response
from api.v1.exceptions import NotFoundClient
from repositories.api.clients import ClientApiRepository

from .schemas import ClientCreate, ClientID, ClientRead

router = APIRouter()

ClientRepository = Annotated[
    ClientApiRepository, Depends(get_repository(ClientApiRepository))
]


@router.get("")
async def list_clients(
    repo: ClientRepository, pagination: Pagination
) -> ResponsePage[ClientRead]:
    items, total = await repo.list_clients(
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return ResponsePage[ClientRead](
        data=TypeAdapter(list[ClientRead]).validate_python(items),
        page=PageMeta(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
        ),
    )


@router.get("/{id}")
async def get_client(client_id: ClientID, repo: ClientRepository) -> Response[ClientRead]:
    client = await repo.get_client(client_id)
    if not client:
        raise NotFoundClient(client_id=client_id)
    return Response[ClientRead](data=ClientRead.model_validate(client))


@router.post("")
async def create_client(
    data: ClientCreate,
    repo: ClientRepository,
) -> Response[ClientRead]:
    client = await repo.create_client(
        name=data.name,
        email=data.email,
    )
    return Response[ClientRead](data=ClientRead.model_validate(client))
