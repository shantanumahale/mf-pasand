"""Fetch fund data from AMFI and mfapi.in."""

from __future__ import annotations

import asyncio
import logging
import re

import httpx

logger = logging.getLogger(__name__)

# Patterns used to filter out unwanted schemes
_EXCLUDE_PATTERNS = re.compile(
    r"(Regular\s+Plan|IDCW|Dividend|Closed\s+Ended|FMP|Institutional|"
    r"Fixed\s+Maturity|Interval\s+Fund)",
    re.IGNORECASE,
)
_DIRECT_GROWTH_PATTERN = re.compile(r"Direct.*Growth|Direct\s+Plan.*Growth", re.IGNORECASE)

AMFI_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt"
MFAPI_BASE = "https://api.mfapi.in/mf"

# Concurrency controls
_SEMAPHORE_LIMIT = 10
_REQUEST_DELAY = 0.1  # seconds between requests


async def fetch_amfi_master(client: httpx.AsyncClient) -> dict[str, str]:
    """Fetch the AMFI NAV master and return a mapping of scheme_code -> ISIN.

    The AMFI file is semicolon-delimited with columns:
    Scheme Code; ISIN Div Payout/Growth; ISIN Div Reinvestment; Scheme Name; NAV; Date
    """
    logger.info("Fetching AMFI master from %s", AMFI_NAV_URL)
    resp = await client.get(AMFI_NAV_URL, timeout=60)
    resp.raise_for_status()

    mapping: dict[str, str] = {}
    for line in resp.text.splitlines():
        parts = line.split(";")
        if len(parts) < 5:
            continue
        scheme_code = parts[0].strip()
        isin = parts[1].strip()
        if scheme_code.isdigit() and isin:
            mapping[scheme_code] = isin

    logger.info("AMFI master: %d scheme_code -> ISIN entries", len(mapping))
    return mapping


async def fetch_all_scheme_codes(client: httpx.AsyncClient) -> list[dict]:
    """GET https://api.mfapi.in/mf -> list of {schemeCode, schemeName}."""
    logger.info("Fetching all scheme codes from mfapi.in")
    resp = await client.get(MFAPI_BASE, timeout=60)
    resp.raise_for_status()
    schemes: list[dict] = resp.json()
    logger.info("Total schemes from mfapi.in: %d", len(schemes))
    return schemes


def is_direct_growth(name: str) -> bool:
    """Return True if the scheme name looks like a direct-plan growth fund."""
    if _EXCLUDE_PATTERNS.search(name):
        return False
    return bool(_DIRECT_GROWTH_PATTERN.search(name))


def filter_schemes(schemes: list[dict]) -> list[dict]:
    """Keep only active, open-ended, direct-plan, growth-option funds."""
    filtered = [s for s in schemes if is_direct_growth(s.get("schemeName", ""))]
    logger.info(
        "Filtered to %d direct/growth schemes (from %d total)",
        len(filtered),
        len(schemes),
    )
    return filtered


async def fetch_nav_history(
    client: httpx.AsyncClient,
    scheme_code: int | str,
    semaphore: asyncio.Semaphore,
) -> dict | None:
    """Fetch NAV history for a single scheme from mfapi.in.

    Returns the full JSON response or None on failure.
    """
    url = f"{MFAPI_BASE}/{scheme_code}"
    async with semaphore:
        await asyncio.sleep(_REQUEST_DELAY)
        try:
            resp = await client.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "SUCCESS":
                return data
            logger.debug("Non-SUCCESS status for scheme %s", scheme_code)
            return None
        except Exception:
            logger.warning("Failed to fetch NAV for scheme %s", scheme_code, exc_info=True)
            return None


async def fetch_all_nav_histories(
    scheme_codes: list[int | str],
    max_concurrency: int = _SEMAPHORE_LIMIT,
) -> dict[str, dict]:
    """Fetch NAV histories for many schemes concurrently.

    Returns a dict of scheme_code (str) -> mfapi response dict.
    """
    semaphore = asyncio.Semaphore(max_concurrency)
    results: dict[str, dict] = {}

    async with httpx.AsyncClient() as client:
        tasks = []
        for code in scheme_codes:
            tasks.append(_fetch_and_store(client, str(code), semaphore, results))
        await asyncio.gather(*tasks)

    logger.info("Fetched NAV history for %d / %d schemes", len(results), len(scheme_codes))
    return results


async def _fetch_and_store(
    client: httpx.AsyncClient,
    code: str,
    semaphore: asyncio.Semaphore,
    store: dict[str, dict],
) -> None:
    data = await fetch_nav_history(client, code, semaphore)
    if data:
        store[code] = data
