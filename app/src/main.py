from api.core.application import create
from api.v1.routers import router

app = create(rest_routers=(router,))
