from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.product.product import Product
    from models.warehouse.warehouse import Warehouse


class StockItem(Base):
    __tablename__ = "stock_item"

    __table_args__ = (
        UniqueConstraint(
            "warehouse_id", "product_id", name="uq_stock_item_warehouse_product"
        ),
        CheckConstraint("quantity >= 0", name="quantity_gte_0"),
        CheckConstraint("reserved_quantity >= 0", name="reserved_quantity_gte_0"),
        CheckConstraint("reserved_quantity <= quantity", name="reserved_lte_quantity"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(nullable=False, default=0)
    reserved_quantity: Mapped[int] = mapped_column(nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", back_populates="stock_items"
    )
    product: Mapped["Product"] = relationship("Product", back_populates="stock_items")

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity
