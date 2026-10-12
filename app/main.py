from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.core.config import settings
from app.database.database import Base, engine
from app.models import Task, User  # noqa: F401 - ensures model metadata is registered
from app.routers import auth, tasks


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    del app
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A production-style RESTful backend API built with FastAPI, featuring "
        "JWT authentication, SQLAlchemy database integration, user management, "
        "protected CRUD operations, validation, and interactive API documentation."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Register, login, and access the authenticated user profile.",
        },
        {
            "name": "Tasks",
            "description": "Protected task management endpoints with per-user ownership.",
        },
        {
            "name": "System",
            "description": "Application status and health endpoints.",
        },
    ],
)

app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(tasks.router, prefix=settings.api_v1_prefix)


@app.get(
    "/",
    tags=["System"],
    summary="API root",
    description="Return basic application metadata and documentation location.",
)
def root() -> dict[str, str]:
    return {
        "name": "FastAPI REST API Backend",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Simple liveness endpoint for deployment and monitoring checks.",
)
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
