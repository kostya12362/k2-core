from api.core.errors.exceptions import BadRequest, NotFound


class QuantityCannotBeLess(BadRequest):
    def __init__(self) -> None:
        super().__init__(message="Quantity cannot be less than reserved quantity")


class StockItemNotFound(NotFound):
    def __init__(self) -> None:
        super().__init__(message="Stock item not found")


class StockItemAlreadyExists(BadRequest):
    def __init__(self) -> None:
        super().__init__(
            message="Stock item already exists for this product in this warehouse"
        )


class WarehouseNotFound(NotFound):
    def __init__(self) -> None:
        super().__init__(message="Warehouse not found")


class WarehouseAlreadyExists(BadRequest):
    def __init__(self) -> None:
        super().__init__(message="Warehouse with this name already exists")
