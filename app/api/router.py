from fastapi import FastAPI

from app.api.endpoints.health import health_router


def include_all_routers(app: FastAPI):
    app.include_router(health_router)
