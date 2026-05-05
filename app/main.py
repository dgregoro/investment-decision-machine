from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    init_db()
    yield


app = FastAPI(
    title="Investment Decision Machine",
    description=("Foundation API for disciplined, human-in-the-loop investment decision support."),
    lifespan=lifespan,
)

app.include_router(health_router)
