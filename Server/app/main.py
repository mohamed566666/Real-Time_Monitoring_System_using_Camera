import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.middleware.rate_limit import limiter, rate_limit_handler
from app.infrastructure.db.database import engine
from app.infrastructure.db.base import Base

from app.presentation.sockets.socket_manager import create_socket_app
from app.presentation.sockets.socket_handlers import register_handlers
from app.infrastructure.workers.session_timeout_worker import run_session_timeout_worker

from app.presentation.controllers.auth_controller import router as auth_router
from app.presentation.controllers.admin_controller import router as admin_router
from app.presentation.controllers.manager_controller import router as manager_router
from app.presentation.controllers.department_controller import router as dept_router
from app.presentation.controllers.employee_controller import router as employee_router
from app.presentation.controllers.session_controller import router as session_router
from app.presentation.controllers.face_embedding_controller import (
    router as embedding_router,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PREFIX = "/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured.")
    register_handlers()
    worker_task = asyncio.create_task(run_session_timeout_worker())
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass


def create_fastapi_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="2.0.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix=PREFIX)
    app.include_router(admin_router, prefix=PREFIX)
    app.include_router(manager_router, prefix=PREFIX)
    app.include_router(dept_router, prefix=PREFIX)
    app.include_router(employee_router, prefix=PREFIX)
    app.include_router(session_router, prefix=PREFIX)
    app.include_router(embedding_router, prefix=PREFIX)

    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok"}

    return app


fastapi_app = create_fastapi_app()
app = create_socket_app(fastapi_app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
