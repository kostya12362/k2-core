from api.core.errors.exceptions import NotFound


class NotFoundClient(NotFound):
    def __init__(self, client_id: int):
        super().__init__(message=f"Not found user with id {client_id}")


class ClientDoesNotExist(NotFound):
    def __init__(self, client_id: int):
        super().__init__(message=f"Client does not exist with id {client_id}")
