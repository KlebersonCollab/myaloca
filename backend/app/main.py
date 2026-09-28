from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.scheduler import start_scheduler, stop_scheduler
from app.db.base import Base
from app.db.init_db import init_initial_data
from app.db.session import async_session_maker, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # 1. Startup: ensure tables exist in dev environment
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Seed initial admin and demo data
    async with async_session_maker() as session:
        await init_initial_data(session)

    # 3. Start auto-release background scheduler
    start_scheduler(interval_seconds=60)

    yield

    # Shutdown
    stop_scheduler()
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="MyAloca - Sistema de Agendamento e Gestão de Baias Híbridas 3D",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development (Vite frontend)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "project": settings.PROJECT_NAME}


@app.get("/", tags=["System"])
async def root() -> dict[str, str]:
    return {
        "message": f"Bem-vindo à API do {settings.PROJECT_NAME}",
        "docs": "/docs",
        "health": "/health",
    }
