"""Main ingestion orchestrator.

Run with:  python -m app.ingestion.ingest
"""

from __future__ import annotations

import asyncio
import logging
import sys

import httpx
from elasticsearch import AsyncElasticsearch

from app.config import settings
from app.ingestion.merge import merge_fund_data
from app.ingestion.sources.amfi import (
    fetch_all_nav_histories,
    fetch_all_scheme_codes,
    fetch_amfi_master,
    filter_schemes,
)
from app.ingestion.sources.kuvera import fetch_all_kuvera_metadata
from app.services.embedding import OpenAIEmbeddingProvider
from app.services.fund_text import fund_to_natural_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Elasticsearch index mapping
INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {
            "scheme_code": {"type": "integer"},
            "scheme_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "isin": {"type": "keyword"},
            "fund_house": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "category": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "fund_type": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "crisil_rating": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "expense_ratio": {"type": "float"},
            "aum_cr": {"type": "float"},
            "min_sip": {"type": "float"},
            "min_lumpsum": {"type": "float"},
            "fund_manager": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "returns_1y": {"type": "float"},
            "returns_3y": {"type": "float"},
            "returns_5y": {"type": "float"},
            "volatility_1y": {"type": "float"},
            "max_drawdown_1y": {"type": "float"},
            "natural_text": {"type": "text"},
            "fund_embedding": {
                "type": "dense_vector",
                "dims": settings.EMBEDDING_DIMS,
                "index": True,
                "similarity": "cosine",
            },
        }
    },
}


async def create_or_recreate_index(es: AsyncElasticsearch) -> None:
    """Create the ES index, deleting it first if it already exists."""
    index = settings.ES_INDEX
    if await es.indices.exists(index=index):
        logger.warning("Deleting existing index '%s'", index)
        await es.indices.delete(index=index)

    await es.indices.create(index=index, body=INDEX_MAPPING)
    logger.info("Created index '%s'", index)


async def bulk_index_funds(
    es: AsyncElasticsearch,
    funds: list[dict],
    batch_size: int = 200,
) -> None:
    """Index funds into Elasticsearch in batches."""
    index = settings.ES_INDEX
    total = len(funds)

    for start in range(0, total, batch_size):
        chunk = funds[start : start + batch_size]
        body: list[dict] = []
        for fund in chunk:
            body.append({"index": {"_index": index, "_id": str(fund["scheme_code"])}})
            body.append(fund)

        resp = await es.bulk(body=body, refresh=False)
        errors = resp.get("errors", False)
        if errors:
            failed = [
                item
                for item in resp.get("items", [])
                if "error" in item.get("index", {})
            ]
            logger.warning(
                "Bulk batch %d-%d had %d errors",
                start,
                start + len(chunk),
                len(failed),
            )
        else:
            logger.info("Indexed batch %d-%d of %d", start, start + len(chunk), total)

    await es.indices.refresh(index=index)
    logger.info("Index refreshed")


async def run_ingestion() -> None:
    """Full ingestion pipeline."""

    logger.info("=== Starting MF Pasand ingestion ===")

    # Step 1: Fetch AMFI master (scheme_code -> ISIN mapping)
    async with httpx.AsyncClient(follow_redirects=True) as client:
        amfi_isin_map = await fetch_amfi_master(client)

    # Step 2: Fetch all scheme codes and filter to direct/growth
    async with httpx.AsyncClient(follow_redirects=True) as client:
        all_schemes = await fetch_all_scheme_codes(client)
    direct_growth = filter_schemes(all_schemes)
    scheme_codes = [str(s["schemeCode"]) for s in direct_growth]
    logger.info("Will process %d direct/growth schemes", len(scheme_codes))

    # Step 3: Fetch NAV histories (async, rate-limited)
    logger.info("Fetching NAV histories...")
    nav_histories = await fetch_all_nav_histories(scheme_codes)

    # Step 4: Build ISIN map for fetched schemes, then fetch Kuvera metadata
    isin_for_kuvera: dict[str, str] = {}
    for code in nav_histories:
        isin = amfi_isin_map.get(code)
        if isin:
            isin_for_kuvera[code] = isin

    logger.info(
        "Fetching Kuvera metadata for %d schemes with ISINs...",
        len(isin_for_kuvera),
    )
    kuvera_metadata = await fetch_all_kuvera_metadata(isin_for_kuvera)

    # Step 5: Merge data + compute metrics
    logger.info("Merging data and computing metrics...")
    merged_funds = merge_fund_data(nav_histories, kuvera_metadata, amfi_isin_map)

    if not merged_funds:
        logger.error("No funds to index -- aborting")
        return

    # Step 6: Generate natural text descriptions
    logger.info("Generating natural text descriptions...")
    for fund in merged_funds:
        fund["natural_text"] = fund_to_natural_text(fund)

    # Step 7: Generate embeddings (batched)
    logger.info("Generating embeddings for %d funds...", len(merged_funds))
    embedder = OpenAIEmbeddingProvider()
    texts = [fund["natural_text"] for fund in merged_funds]
    embeddings = await embedder.embed_batch(texts)

    for fund, emb in zip(merged_funds, embeddings):
        fund["fund_embedding"] = emb

    # Step 8: Create ES index with proper mapping
    es = AsyncElasticsearch(hosts=[f"http://{settings.ES_HOST}"])
    try:
        await create_or_recreate_index(es)

        # Step 9: Bulk index documents
        await bulk_index_funds(es, merged_funds)

        count_resp = await es.count(index=settings.ES_INDEX)
        logger.info(
            "=== Ingestion complete: %d documents indexed ===",
            count_resp.get("count", 0),
        )
    finally:
        await es.close()


if __name__ == "__main__":
    asyncio.run(run_ingestion())
