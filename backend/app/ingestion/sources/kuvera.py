"""Fetch fund metadata from mf.captnemo.in (Kuvera-sourced data)."""

from __future__ import annotations

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

KUVERA_BASE = "https://mf.captnemo.in/kuvera"

_SEMAPHORE_LIMIT = 5
_REQUEST_DELAY = 0.2  # be gentle with the free API


async def fetch_kuvera_metadata(
    client: httpx.AsyncClient,
    isin: str,
    semaphore: asyncio.Semaphore,
) -> dict | None:
    """Fetch metadata for a single ISIN from mf.captnemo.in.

    Returns a dict of extracted fields, or None on failure / 404.
    """
    url = f"{KUVERA_BASE}/{isin}"
    async with semaphore:
        await asyncio.sleep(_REQUEST_DELAY)
        try:
            resp = await client.get(url, timeout=30)
            if resp.status_code == 404:
                logger.debug("Kuvera 404 for ISIN %s", isin)
                return None
            resp.raise_for_status()
            raw = resp.json()

            # API returns a JSON array — take the first entry
            if isinstance(raw, list):
                if not raw:
                    return None
                data = raw[0]
            else:
                data = raw

            extracted: dict = {}

            # Map Kuvera fields to our schema
            if data.get("category"):
                extracted["category"] = data["category"]
            if data.get("fund_category"):
                extracted["fund_category"] = data["fund_category"]
            if data.get("fund_type"):
                extracted["fund_type"] = data["fund_type"]
            if data.get("fund_name"):
                extracted["fund_house"] = data["fund_name"]
            if data.get("fund_manager"):
                extracted["fund_manager"] = data["fund_manager"]
            if data.get("crisil_rating"):
                extracted["crisil_rating"] = data["crisil_rating"]
            if data.get("maturity_type"):
                extracted["maturity_type"] = data["maturity_type"]
            if data.get("fund_rating") is not None:
                extracted["fund_rating"] = data["fund_rating"]

            # Expense ratio comes as a string
            er = data.get("expense_ratio")
            if er is not None:
                try:
                    extracted["expense_ratio"] = float(er)
                except (TypeError, ValueError):
                    pass

            # AUM in lakhs from API — convert to crores
            aum = data.get("aum")
            if aum is not None:
                try:
                    extracted["aum_cr"] = round(float(aum) / 100, 2)
                except (TypeError, ValueError):
                    pass

            # SIP and lumpsum minimums
            sip_min = data.get("sip_min")
            if sip_min is not None:
                try:
                    extracted["min_sip"] = float(sip_min)
                except (TypeError, ValueError):
                    pass

            lump_min = data.get("lump_min")
            if lump_min is not None:
                try:
                    extracted["min_lumpsum"] = float(lump_min)
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

    async with httpx.AsyncClient(follow_redirects=True) as client:
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
