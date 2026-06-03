from api.core.errors.exceptions import BadRequest, NotFound


class OrderNotFound(NotFound):
    def __init__(self, order_id: int) -> None:
        super().__init__(
            message=f"Order with id {order_id} not found",
            code="ORDER_NOT_FOUND",
        )


class OrderMustContainItems(BadRequest):
    def __init__(self) -> None:
        super().__init__(
            message="Order must contain at least one item",
            code="ORDER_MUST_CONTAIN_ITEMS",
        )


class ProductDoesNotExist(BadRequest):
    def __init__(self, product_id: int) -> None:
        super().__init__(
            message=f"Product with id {product_id} does not exist",
            code="PRODUCT_DOES_NOT_EXIST",
        )


class NotEnoughProductInStock(BadRequest):
    def __init__(self, product_id: int) -> None:
        super().__init__(
            message=f"Not enough product {product_id} in stock",
            code="NOT_ENOUGH_PRODUCT_IN_STOCK",
        )
