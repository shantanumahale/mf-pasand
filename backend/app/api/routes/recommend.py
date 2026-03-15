"""POST /recommend -- personalised mutual fund recommendations."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_embedding_provider, get_es_client
from app.config import settings
from app.models.fund import FundRecommendation
from app.models.persona import UserPersona
from app.services.fund_text import persona_to_natural_text
from app.services.search import build_recommendation_query, parse_recommendation_hits

logger = logging.getLogger(__name__)
router = APIRouter(tags=["recommendations"])

TOP_K_CANDIDATES = 50
TOP_N_RESULTS = 10


@router.post("/recommend", response_model=list[FundRecommendation])
async def recommend_funds(persona: UserPersona) -> list[FundRecommendation]:
    """Return the top mutual fund recommendations for a given investor persona."""

    es = get_es_client()
    embedder = get_embedding_provider()

    # 1. Convert persona to natural language
    persona_text = persona_to_natural_text(persona)
    logger.info("Persona text: %s", persona_text[:200])

    # 2. Generate embedding
    try:
        embedding = await embedder.embed_text(persona_text)
    except Exception as exc:
        logger.error("Embedding generation failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=502, detail="Failed to generate persona embedding"
        ) from exc

    # 3. Build and execute ES query
    query = build_recommendation_query(embedding, persona, top_k=TOP_K_CANDIDATES)
    try:
        response = await es.search(index=settings.ES_INDEX, body=query)
    except Exception as exc:
        logger.error("Elasticsearch search failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=502, detail="Search backend unavailable"
        ) from exc

    # 4. Parse and return top N
    hits = response.get("hits", {}).get("hits", [])
    recommendations = parse_recommendation_hits(hits)
    return recommendations[:TOP_N_RESULTS]
