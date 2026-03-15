"""Fund-related pydantic models."""

from typing import Optional

from pydantic import BaseModel


class FundBase(BaseModel):
    """Core identifying fields for a mutual fund scheme."""

    scheme_code: int
    scheme_name: str
    isin: Optional[str] = None
    fund_house: Optional[str] = None
    category: Optional[str] = None
    fund_type: Optional[str] = None


class FundMetrics(BaseModel):
    """Performance and risk metrics computed from NAV history."""

    returns_1y: Optional[float] = None
    returns_3y: Optional[float] = None
    returns_5y: Optional[float] = None
    volatility_1y: Optional[float] = None
    max_drawdown_1y: Optional[float] = None


class FundDetail(FundBase, FundMetrics):
    """Full fund record including metadata and computed metrics."""

    crisil_rating: Optional[str] = None
    expense_ratio: Optional[float] = None
    aum_cr: Optional[float] = None
    min_sip: Optional[float] = None
    min_lumpsum: Optional[float] = None
    fund_manager: Optional[str] = None
    natural_text: Optional[str] = None


class FundRecommendation(FundDetail):
    """Fund detail augmented with a similarity score from vector search."""

    similarity_score: float = 0.0


class FundListResponse(BaseModel):
    """Paginated list of funds."""

    funds: list[FundDetail]
    total: int
    page: int
    page_size: int
