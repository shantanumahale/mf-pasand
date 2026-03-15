"""Embedding generation with a swappable provider abstraction."""

import logging
from abc import ABC, abstractmethod

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


def get_embedding_provider() -> EmbeddingProvider:
    """Factory that returns the configured embedding provider."""
    return OpenAIEmbeddingProvider()
