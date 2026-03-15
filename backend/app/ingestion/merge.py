"""Merge AMFI NAV data with Kuvera metadata and compute derived metrics."""

from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _parse_nav_entries(nav_data: list[dict]) -> list[tuple[datetime, float]]:
    """Parse mfapi.in NAV entries into sorted (date, nav) pairs.

    mfapi returns entries as [{date: "DD-MM-YYYY", nav: "123.45"}, ...],
    newest first.
    """
    parsed: list[tuple[datetime, float]] = []
    for entry in nav_data:
        try:
            dt = datetime.strptime(entry["date"], "%d-%m-%Y")
            nav = float(entry["nav"])
            parsed.append((dt, nav))
        except (KeyError, ValueError):
            continue

    # Sort oldest first
    parsed.sort(key=lambda x: x[0])
    return parsed


def _compute_cagr(start_nav: float, end_nav: float, years: float) -> float | None:
    """Compute Compound Annual Growth Rate."""
    if start_nav <= 0 or years <= 0:
        return None
    ratio = end_nav / start_nav
    if ratio <= 0:
        return None
    return (ratio ** (1.0 / years) - 1.0) * 100.0


def _compute_returns(
    navs: list[tuple[datetime, float]],
) -> dict[str, float | None]:
    """Compute 1Y, 3Y, 5Y CAGR from NAV time series."""
    if not navs:
        return {"returns_1y": None, "returns_3y": None, "returns_5y": None}

    latest_date, latest_nav = navs[-1]
    results: dict[str, float | None] = {}

    for label, years in [("returns_1y", 1), ("returns_3y", 3), ("returns_5y", 5)]:
        target_date = latest_date - timedelta(days=years * 365)
        # Find the NAV closest to target_date
        closest = min(navs, key=lambda x: abs((x[0] - target_date).days))
        delta_days = abs((closest[0] - target_date).days)

        if delta_days > 30:  # too far from the target date
            results[label] = None
        else:
            actual_years = (latest_date - closest[0]).days / 365.25
            results[label] = _compute_cagr(closest[1], latest_nav, actual_years)

    return results


def _compute_volatility_and_drawdown(
    navs: list[tuple[datetime, float]],
) -> dict[str, float | None]:
    """Compute annualised volatility and max drawdown over the last 1 year."""
    if len(navs) < 20:
        return {"volatility_1y": None, "max_drawdown_1y": None}

    latest_date = navs[-1][0]
    cutoff = latest_date - timedelta(days=365)

    # Filter to last 1 year
    recent = [(d, n) for d, n in navs if d >= cutoff]
    if len(recent) < 20:
        return {"volatility_1y": None, "max_drawdown_1y": None}

    # Daily returns
    daily_returns: list[float] = []
    for i in range(1, len(recent)):
        prev_nav = recent[i - 1][1]
        curr_nav = recent[i][1]
        if prev_nav > 0:
            daily_returns.append((curr_nav - prev_nav) / prev_nav)

    if not daily_returns:
        return {"volatility_1y": None, "max_drawdown_1y": None}

    # Annualised volatility (std dev * sqrt(252))
    mean_ret = sum(daily_returns) / len(daily_returns)
    variance = sum((r - mean_ret) ** 2 for r in daily_returns) / len(daily_returns)
    std_dev = math.sqrt(variance)
    annualised_vol = std_dev * math.sqrt(252) * 100.0  # as percentage

    # Max drawdown
    peak = recent[0][1]
    max_dd = 0.0
    for _, nav in recent:
        if nav > peak:
            peak = nav
        if peak > 0:
            drawdown = (peak - nav) / peak * 100.0
            if drawdown > max_dd:
                max_dd = drawdown

    return {
        "volatility_1y": round(annualised_vol, 2),
        "max_drawdown_1y": round(max_dd, 2),
    }


def merge_fund_data(
    nav_histories: dict[str, dict],
    kuvera_metadata: dict[str, dict],
    amfi_isin_map: dict[str, str],
) -> list[dict]:
    """Merge AMFI NAV data with Kuvera metadata and compute derived metrics.

    Args:
        nav_histories: scheme_code -> mfapi response dict
        kuvera_metadata: scheme_code -> kuvera metadata dict
        amfi_isin_map: scheme_code -> ISIN

    Returns:
        List of merged fund dicts ready for indexing.
    """
    merged: list[dict] = []

    for scheme_code, nav_resp in nav_histories.items():
        meta_info = nav_resp.get("meta", {})
        nav_entries = nav_resp.get("data", [])

        fund: dict = {
            "scheme_code": int(scheme_code),
            "scheme_name": meta_info.get("scheme_name", ""),
            "isin": amfi_isin_map.get(scheme_code),
            "fund_house": meta_info.get("fund_house"),
        }

        # Merge Kuvera metadata
        kuvera = kuvera_metadata.get(scheme_code, {})
        fund["category"] = kuvera.get("category") or kuvera.get("fund_category")
        fund["fund_type"] = kuvera.get("fund_type")
        fund["crisil_rating"] = kuvera.get("crisil_rating")
        fund["expense_ratio"] = _safe_float(kuvera.get("expense_ratio"))
        fund["aum_cr"] = _safe_float(kuvera.get("aum_cr") or kuvera.get("aum"))
        fund["min_sip"] = _safe_float(kuvera.get("min_sip"))
        fund["min_lumpsum"] = _safe_float(kuvera.get("min_lumpsum"))
        fund["fund_manager"] = kuvera.get("fund_manager")
        fund["fund_house"] = kuvera.get("fund_house") or fund["fund_house"]

        # Compute metrics from NAV history
        parsed_navs = _parse_nav_entries(nav_entries)
        returns = _compute_returns(parsed_navs)
        vol_dd = _compute_volatility_and_drawdown(parsed_navs)

        fund.update(returns)
        fund.update(vol_dd)

        merged.append(fund)

    logger.info("Merged %d fund records", len(merged))
    return merged


def _safe_float(val) -> float | None:
    """Attempt to convert a value to float, returning None on failure."""
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
