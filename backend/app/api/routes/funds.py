"""GET /funds -- fund listing and detail endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import get_es_client
from app.config import settings
from app.models.fund import FundDetail, FundListResponse
from app.services.search import build_fund_list_query, parse_fund_hits

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/funds", tags=["funds"])


@router.get("", response_model=FundListResponse)
async def list_funds(
    category: str | None = Query(None, description="Filter by fund category"),
    fund_type: str | None = Query(None, description="Filter by fund type (Equity, Debt, Hybrid, etc.)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> FundListResponse:
    """Return a paginated list of mutual funds with optional filters."""

    es = get_es_client()
    query = build_fund_list_query(
        category=category,
        fund_type=fund_type,
        page=page,
        page_size=page_size,
    )

    try:
        response = await es.search(index=settings.ES_INDEX, body=query)
    except Exception as exc:
        logger.error("Elasticsearch query failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=502, detail="Search backend unavailable"
        ) from exc

    hits = response.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    funds = parse_fund_hits(hits.get("hits", []))

    return FundListResponse(
        funds=funds,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{scheme_code}", response_model=FundDetail)
async def get_fund(scheme_code: int) -> FundDetail:
    """Return full details for a single fund by scheme code."""

    es = get_es_client()

    try:
        response = await es.search(
            index=settings.ES_INDEX,
            body={
                "query": {"term": {"scheme_code": scheme_code}},
                "size": 1,
                "_source": {"excludes": ["fund_embedding"]},
            },
        )
    except Exception as exc:
        logger.error("Elasticsearch query failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=502, detail="Search backend unavailable"
        ) from exc

    hits = response.get("hits", {}).get("hits", [])
    if not hits:
        raise HTTPException(status_code=404, detail="Fund not found")

    funds = parse_fund_hits(hits)
    return funds[0]
