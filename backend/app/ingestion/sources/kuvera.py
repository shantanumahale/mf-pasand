"""Fetch fund metadata from mf.captnemo.in (Kuvera-sourced data)."""

from __future__ import annotations

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

KUVERA_BASE = "https://mf.captnemo.in"

_SEMAPHORE_LIMIT = 5
_REQUEST_DELAY = 0.2  # be gentle with the free API

# Fields to extract from the Kuvera response
_FIELDS = [
    "aum",
    "category",
    "crisil_rating",
    "expense_ratio",
    "fund_category",
    "fund_house",
    "fund_manager",
    "fund_type",
    "fund_rating",
    "min_sip",
    "min_lumpsum",
    "maturity_type",
]


async def fetch_kuvera_metadata(
    client: httpx.AsyncClient,
    isin: str,
    semaphore: asyncio.Semaphore,
) -> dict | None:
    """Fetch metadata for a single ISIN from mf.captnemo.in.

    Returns a dict of extracted fields, or None on failure / 404.
    """
    url = f"{KUVERA_BASE}/{isin}.json"
    async with semaphore:
        await asyncio.sleep(_REQUEST_DELAY)
        try:
            resp = await client.get(url, timeout=30)
            if resp.status_code == 404:
                logger.debug("Kuvera 404 for ISIN %s", isin)
                return None
            resp.raise_for_status()
            data = resp.json()

            extracted: dict = {}
            for field in _FIELDS:
                val = data.get(field)
                if val is not None:
                    extracted[field] = val

            # Normalise AUM to crores if present
            aum = extracted.get("aum")
            if aum is not None:
                try:
                    extracted["aum_cr"] = float(aum)
                except (TypeError, ValueError):
                    pass

            return extracted if extracted else None

        except Exception:
            logger.warning(
                "Failed to fetch Kuvera metadata for ISIN %s", isin, exc_info=True
            )
            return None


async def fetch_all_kuvera_metadata(
    isin_map: dict[str, str],
    max_concurrency: int = _SEMAPHORE_LIMIT,
) -> dict[str, dict]:
    """Fetch Kuvera metadata for many ISINs concurrently.

    Args:
        isin_map: scheme_code -> ISIN mapping
        max_concurrency: max concurrent requests

    Returns:
        scheme_code -> metadata dict
    """
    semaphore = asyncio.Semaphore(max_concurrency)
    results: dict[str, dict] = {}

    async with httpx.AsyncClient() as client:
        tasks = []
        for scheme_code, isin in isin_map.items():
            tasks.append(
                _fetch_and_store(client, scheme_code, isin, semaphore, results)
            )
        await asyncio.gather(*tasks)

    logger.info(
        "Fetched Kuvera metadata for %d / %d ISINs",
        len(results),
        len(isin_map),
    )
    return results


async def _fetch_and_store(
    client: httpx.AsyncClient,
    scheme_code: str,
    isin: str,
    semaphore: asyncio.Semaphore,
    store: dict[str, dict],
) -> None:
    meta = await fetch_kuvera_metadata(client, isin, semaphore)
    if meta:
        store[scheme_code] = meta
