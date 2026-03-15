"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import close_es_client, get_es_client
from app.api.routes import funds, recommend

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown."""
    logger.info("Starting up MF Pasand backend")
    yield
    await close_es_client()
    logger.info("Shutdown complete")


app = FastAPI(
    title="MF Pasand",
    description="Mutual Fund Recommender API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS -- wide open for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(recommend.router)
app.include_router(funds.router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness check that also verifies Elasticsearch connectivity."""
    try:
        es = get_es_client()
        info = await es.info()
        cluster_name = info.get("cluster_name", "unknown")
        return {"status": "healthy", "elasticsearch": cluster_name}
    except Exception as exc:
        logger.warning("Health check failed: %s", exc)
        return {"status": "degraded", "elasticsearch": str(exc)}
