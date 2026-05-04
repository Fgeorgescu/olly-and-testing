from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1 import health
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.version)

Instrumentator().instrument(app).expose(app)
app.include_router(health.router, prefix="/api/v1")
