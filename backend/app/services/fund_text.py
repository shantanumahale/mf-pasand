"""Convert structured fund data and user personas into natural language."""

from __future__ import annotations

from app.models.persona import UserPersona


def _fmt_pct(value: float | None) -> str | None:
    if value is None:
        return None
    return f"{value:.2f}%"


def _interpret_expense_ratio(er: float) -> str:
    if er <= 0.5:
        return "very low"
    if er <= 1.0:
        return "low"
    if er <= 1.5:
        return "moderate"
    return "high"


def _interpret_volatility(vol: float) -> str:
    if vol <= 10:
        return "low"
    if vol <= 20:
        return "moderate"
    if vol <= 30:
        return "high"
    return "very high"


def _interpret_aum(aum: float) -> str:
    if aum >= 10000:
        return "very large"
    if aum >= 5000:
        return "large"
    if aum >= 1000:
        return "mid-sized"
    return "small"


def fund_to_natural_text(fund: dict) -> str:
    """Convert a fund data dictionary into a natural-language paragraph.

    Missing fields are silently skipped. The output is roughly 100-200 words,
    covering identity, risk, cost, performance, and investment minimums.
    """
    parts: list[str] = []

    name = fund.get("scheme_name")
    if name:
        parts.append(f"{name} is a mutual fund scheme")

    fund_house = fund.get("fund_house")
    if fund_house:
        parts.append(f"offered by {fund_house}")

    category = fund.get("category")
    fund_type = fund.get("fund_type")
    if category and fund_type:
        parts.append(f"classified under the {category} category within the {fund_type} segment")
    elif category:
        parts.append(f"classified under the {category} category")
    elif fund_type:
        parts.append(f"in the {fund_type} segment")

    # Combine the opening sentence
    opening = " ".join(parts) + "." if parts else ""

    details: list[str] = []

    crisil = fund.get("crisil_rating")
    if crisil:
        details.append(f"It carries a CRISIL rating of {crisil}")

    er = fund.get("expense_ratio")
    if er is not None:
        label = _interpret_expense_ratio(er)
        details.append(f"The expense ratio is {er:.2f}%, which is considered {label}")

    aum = fund.get("aum_cr")
    if aum is not None:
        label = _interpret_aum(aum)
        details.append(
            f"With an AUM of approximately {aum:,.0f} crores, it is a {label} fund"
        )

    # Returns
    ret_parts: list[str] = []
    r1 = fund.get("returns_1y")
    if r1 is not None:
        ret_parts.append(f"{r1:.2f}% over one year")
    r3 = fund.get("returns_3y")
    if r3 is not None:
        ret_parts.append(f"{r3:.2f}% over three years")
    r5 = fund.get("returns_5y")
    if r5 is not None:
        ret_parts.append(f"{r5:.2f}% over five years")
    if ret_parts:
        details.append(
            "The fund has delivered annualised returns of " + ", ".join(ret_parts)
        )

    vol = fund.get("volatility_1y")
    if vol is not None:
        # volatility is stored as a decimal (e.g. 0.15 = 15%)
        vol_pct = vol * 100 if vol < 1 else vol
        label = _interpret_volatility(vol_pct)
        details.append(
            f"Its one-year annualised volatility stands at {vol_pct:.2f}%, indicating {label} volatility"
        )

    mdd = fund.get("max_drawdown_1y")
    if mdd is not None:
        # max_drawdown is stored as a decimal (e.g. -0.08 = -8%)
        mdd_pct = mdd * 100 if abs(mdd) < 1 else mdd
        details.append(
            f"The maximum drawdown over the past year was {mdd_pct:.2f}%"
        )

    sip = fund.get("min_sip")
    lump = fund.get("min_lumpsum")
    if sip is not None and lump is not None:
        details.append(
            f"Investors can start a SIP with as little as {sip:,.0f} rupees "
            f"or make a lump-sum investment starting at {lump:,.0f} rupees"
        )
    elif sip is not None:
        details.append(
            f"The minimum SIP amount is {sip:,.0f} rupees"
        )
    elif lump is not None:
        details.append(
            f"The minimum lump-sum investment is {lump:,.0f} rupees"
        )

    mgr = fund.get("fund_manager")
    if mgr:
        details.append(f"The fund is managed by {mgr}")

    body = ". ".join(details) + "." if details else ""
    return f"{opening} {body}".strip()


def persona_to_natural_text(persona: UserPersona) -> str:
    """Convert a UserPersona into a natural-language description.

    Only fields that are not None are included.
    """

    # Build the opening sentence as a single flowing clause
    opening_parts: list[str] = [f"A {persona.age}-year-old investor"]

    if persona.annual_income is not None:
        opening_parts.append(
            f"with an annual income of approximately {persona.annual_income:.0f} lakhs"
        )

    horizon_map = {
        "short": "a short-term horizon (up to 3 years)",
        "medium": "a medium-term horizon (3 to 7 years)",
        "long": "a long-term horizon (7 years or more)",
    }
    opening_parts.append(
        f"looking to invest over {horizon_map.get(persona.investment_horizon, persona.investment_horizon)}"
    )

    risk_map = {
        "low": "low risk appetite, preferring capital preservation",
        "moderate": "moderate risk appetite, balancing growth and safety",
        "high": "high risk appetite, comfortable with market fluctuations",
        "very_high": "very high risk appetite, seeking aggressive growth",
    }
    opening_parts.append(
        f"with {risk_map.get(persona.risk_appetite, persona.risk_appetite)}"
    )

    # The opening is one sentence joined by commas/spaces
    opening = " ".join(opening_parts)

    # Remaining details are separate sentences
    sentences: list[str] = [opening]

    goal_map = {
        "wealth_creation": "long-term wealth creation",
        "tax_saving": "saving on taxes under Section 80C",
        "retirement": "building a retirement corpus",
        "child_education": "funding a child's education",
        "emergency_fund": "building an emergency fund with high liquidity",
        "regular_income": "generating regular income from investments",
    }
    goal_label = goal_map.get(persona.investment_goal, persona.investment_goal)
    sentences.append(f"The primary investment goal is {goal_label}")

    if persona.monthly_sip_budget is not None:
        sentences.append(
            f"The monthly SIP budget is approximately {persona.monthly_sip_budget:,.0f} rupees"
        )

    if persona.lumpsum_available is not None:
        sentences.append(
            f"There is a lump-sum amount of approximately {persona.lumpsum_available:,.0f} rupees available for investment"
        )

    if persona.existing_investments:
        sentences.append(
            f"Existing investments include: {persona.existing_investments}"
        )

    if persona.preferences:
        sentences.append(f"Additional preferences: {persona.preferences}")

    return ". ".join(sentences) + "."
