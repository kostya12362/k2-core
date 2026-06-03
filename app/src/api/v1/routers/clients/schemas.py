from typing import Annotated

from fastapi import Path
from pydantic import EmailStr

from api.core.schemas.base import PublicSchema

ClientID = Annotated[int, Path(..., ge=1, alias="id")]


class ClientCreate(PublicSchema):
    name: str
    email: EmailStr


class ClientRead(ClientCreate):
    id: int
