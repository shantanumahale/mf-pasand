"""Shared FastAPI dependencies for Elasticsearch and embedding clients."""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from elasticsearch import AsyncElasticsearch

from app.config import settings
from app.services.embedding import EmbeddingProvider, OpenAIEmbeddingProvider

logger = logging.getLogger(__name__)

# Module-level singletons, initialised on first use.
_es_client: AsyncElasticsearch | None = None
_embedding_provider: EmbeddingProvider | None = None


def get_es_client() -> AsyncElasticsearch:
    """Return (or lazily create) a singleton async Elasticsearch client."""
    global _es_client
    if _es_client is None:
        _es_client = AsyncElasticsearch(
            hosts=[f"http://{settings.ES_HOST}"],
            request_timeout=30,
        )
        logger.info("Elasticsearch client created for %s", settings.ES_HOST)
    return _es_client


def get_embedding_provider() -> EmbeddingProvider:
    """Return (or lazily create) a singleton embedding provider."""
    global _embedding_provider
    if _embedding_provider is None:
        _embedding_provider = OpenAIEmbeddingProvider()
        logger.info("OpenAI embedding provider initialised")
    return _embedding_provider


async def close_es_client() -> None:
    """Cleanly close the Elasticsearch client."""
    global _es_client
    if _es_client is not None:
        await _es_client.close()
        _es_client = None
        logger.info("Elasticsearch client closed")
