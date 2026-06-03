from typing import TYPE_CHECKING

from sqlalchemy import VARCHAR, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.order.order import Order


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(128), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(256), unique=True, nullable=False)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="client")

    def __repr__(self) -> str:
        return f"<Client id={self.id} name={self.name!r}>"
