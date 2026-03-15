"""Embedding generation with a swappable provider abstraction."""

import asyncio
import logging
from abc import ABC, abstractmethod
from functools import partial

import openai

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text."""
        ...

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of texts."""
        ...


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI-backed embedding provider."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self._model = model or settings.EMBEDDING_MODEL
        self._client = openai.AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)

    async def embed_text(self, text: str) -> list[float]:
        response = await self._client.embeddings.create(
            input=[text],
            model=self._model,
        )
        return response.data[0].embedding

    async def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 100,
    ) -> list[list[float]]:
        """Embed texts in batches to stay within API limits."""
        all_embeddings: list[list[float]] = []

        for start in range(0, len(texts), batch_size):
            chunk = texts[start : start + batch_size]
            logger.info(
                "Embedding batch %d-%d of %d",
                start,
                start + len(chunk),
                len(texts),
            )
            response = await self._client.embeddings.create(
                input=chunk,
                model=self._model,
            )
            # OpenAI returns results in the same order as input
            all_embeddings.extend([d.embedding for d in response.data])

        return all_embeddings


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local sentence-transformers embedding provider (no API key needed)."""

    def __init__(self, model: str | None = None) -> None:
        from sentence_transformers import SentenceTransformer

        self._model_name = model or settings.EMBEDDING_MODEL
        logger.info("Loading local embedding model '%s'...", self._model_name)
        self._model = SentenceTransformer(self._model_name)
        logger.info("Local embedding model loaded")

    def _encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
        return embeddings.tolist()

    async def embed_text(self, text: str) -> list[float]:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, partial(self._encode, [text]))
        return result[0]

    async def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 256,
    ) -> list[list[float]]:
        """Embed texts in batches using the local model."""
        all_embeddings: list[list[float]] = []

        for start in range(0, len(texts), batch_size):
            chunk = texts[start : start + batch_size]
            logger.info(
                "Embedding batch %d-%d of %d",
                start,
                start + len(chunk),
                len(texts),
            )
            loop = asyncio.get_running_loop()
            batch_embs = await loop.run_in_executor(
                None, partial(self._encode, chunk)
            )
            all_embeddings.extend(batch_embs)

        return all_embeddings


def get_embedding_provider() -> EmbeddingProvider:
    """Factory that returns the configured embedding provider."""
    if settings.EMBEDDING_PROVIDER == "openai":
        return OpenAIEmbeddingProvider()
    return LocalEmbeddingProvider()
