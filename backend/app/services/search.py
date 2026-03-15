"""Elasticsearch query builders and result parsers."""

from __future__ import annotations

import logging
from typing import Any

from app.models.fund import FundDetail, FundRecommendation
from app.models.persona import UserPersona

logger = logging.getLogger(__name__)

# Categories considered "liquid-like" for emergency_fund goal
LIQUID_CATEGORIES = {"Liquid", "Overnight", "Ultra Short Duration"}


def build_recommendation_query(
    embedding: list[float],
    persona: UserPersona,
    top_k: int = 50,
) -> dict[str, Any]:
    """Build an Elasticsearch kNN query with hard filters derived from the persona."""

    filters: list[dict[str, Any]] = []

    # Risk-based filter: conservative investors should only see low-risk rated funds
    if persona.risk_appetite == "low":
        filters.append(
            {"terms": {"crisil_rating.keyword": ["Low", "Low to Moderate"]}}
        )

    # Goal-based filters
    if persona.investment_goal == "tax_saving":
        filters.append({"term": {"category.keyword": "ELSS"}})

    if persona.investment_goal == "emergency_fund":
        filters.append({"term": {"fund_type.keyword": "Debt"}})
        filters.append(
            {"terms": {"category.keyword": list(LIQUID_CATEGORIES)}}
        )

    # Budget-based filters
    if persona.monthly_sip_budget is not None:
        filters.append(
            {"range": {"min_sip": {"lte": persona.monthly_sip_budget}}}
        )

    if persona.lumpsum_available is not None:
        filters.append(
            {"range": {"min_lumpsum": {"lte": persona.lumpsum_available}}}
        )

    query: dict[str, Any] = {
        "knn": {
            "field": "fund_embedding",
            "query_vector": embedding,
            "k": top_k,
            "num_candidates": top_k * 4,
            "similarity": 0.5,
        },
        "size": top_k,
        "_source": {"excludes": ["fund_embedding"]},
    }

    if filters:
        query["knn"]["filter"] = {"bool": {"must": filters}}

    return query


def build_fund_list_query(
    category: str | None = None,
    fund_type: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """Build a paginated fund listing query with optional filters."""

    filters: list[dict[str, Any]] = []

    if category:
        filters.append({"term": {"category.keyword": category}})
    if fund_type:
        filters.append({"term": {"fund_type.keyword": fund_type}})

    body: dict[str, Any] = {
        "from": (page - 1) * page_size,
        "size": page_size,
        "_source": {"excludes": ["fund_embedding"]},
        "sort": [{"aum_cr": {"order": "desc", "missing": "_last"}}],
    }

    if filters:
        body["query"] = {"bool": {"must": filters}}
    else:
        body["query"] = {"match_all": {}}

    return body


def parse_recommendation_hits(
    hits: list[dict[str, Any]],
) -> list[FundRecommendation]:
    """Convert raw Elasticsearch hits into FundRecommendation objects."""

    results: list[FundRecommendation] = []
    for hit in hits:
        source = hit["_source"]
        score = hit.get("_score", 0.0)
        try:
            rec = FundRecommendation(similarity_score=score, **source)
            results.append(rec)
        except Exception:
            logger.warning(
                "Skipping malformed hit id=%s", hit.get("_id"), exc_info=True
            )
    return results


def parse_fund_hits(hits: list[dict[str, Any]]) -> list[FundDetail]:
    """Convert raw Elasticsearch hits into FundDetail objects."""

    results: list[FundDetail] = []
    for hit in hits:
        source = hit["_source"]
        try:
            results.append(FundDetail(**source))
        except Exception:
            logger.warning(
                "Skipping malformed hit id=%s", hit.get("_id"), exc_info=True
            )
    return results
