from enum import StrEnum


class OrderStatus(StrEnum):
    created = "created"
    cancelled = "cancelled"


class ProductStatus(StrEnum):
    available = "available"
    unavailable = "unavailable"
