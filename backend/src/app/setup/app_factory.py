"""
Фабрика приложения для создания и настройки FastAPI приложения
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.app.infrastructure.persistence.database import engine
from src.app.presentation.http.controllers.api_data_controller import router as api_data_router
from src.app.presentation.http.errors.handlers import setup_exception_handlers
from src.app.setup.config.settings import get_settings

settings = get_settings()

ENVIRONMENT = settings.ENVIRONMENT
SHOW_DOCS_ENVIRONMENT = ("local", "staging")

app_configs = {
    "title": settings.PROJECT_NAME,
    "version": settings.VERSION,
}

if ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_configs["openapi_url"] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения"""
    async with engine.begin() as conn:
        from src.app.infrastructure.persistence.database import Base

        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(**app_configs, lifespan=lifespan)

if ENVIRONMENT == "local":
    cors_origins = ["*"]
    allow_credentials = False
else:
    cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
    if not cors_origins:
        raise ValueError("CORS_ORIGINS must be set in production")
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

setup_exception_handlers(app)

app.include_router(api_data_router)


@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {"status": "ok"}
