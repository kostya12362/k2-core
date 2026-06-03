from api.core.errors.exceptions import BadRequest, NotFound


class ProductWithSKUAlreadyExist(BadRequest):
    def __init__(self, sku: str) -> None:
        super().__init__(
            message=f"Product with this SKU {sku} already exists",
        )


class ProductNotFound(NotFound):
    def __init__(self, product_id: int) -> None:
        super().__init__(
            message=f"Product with not found {product_id}",
        )
