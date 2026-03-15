"""User persona model for mutual fund recommendations."""

from typing import Optional

from pydantic import BaseModel, field_validator

VALID_HORIZONS = {"short", "medium", "long"}
VALID_RISK_APPETITES = {"low", "moderate", "high", "very_high"}
VALID_GOALS = {
    "wealth_creation",
    "tax_saving",
    "retirement",
    "child_education",
    "emergency_fund",
    "regular_income",
}


class UserPersona(BaseModel):
    """Captures an investor's profile for generating personalised recommendations."""

    age: int
    annual_income: Optional[float] = None  # in lakhs
    investment_horizon: str  # "short", "medium", "long"
    risk_appetite: str  # "low", "moderate", "high", "very_high"
    investment_goal: str
    monthly_sip_budget: Optional[float] = None
    lumpsum_available: Optional[float] = None
    existing_investments: Optional[str] = None
    preferences: Optional[str] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if not 18 <= v <= 100:
            raise ValueError("Age must be between 18 and 100")
        return v

    @field_validator("investment_horizon")
    @classmethod
    def validate_horizon(cls, v: str) -> str:
        if v not in VALID_HORIZONS:
            raise ValueError(
                f"investment_horizon must be one of {sorted(VALID_HORIZONS)}"
            )
        return v

    @field_validator("risk_appetite")
    @classmethod
    def validate_risk(cls, v: str) -> str:
        if v not in VALID_RISK_APPETITES:
            raise ValueError(
                f"risk_appetite must be one of {sorted(VALID_RISK_APPETITES)}"
            )
        return v

    @field_validator("investment_goal")
    @classmethod
    def validate_goal(cls, v: str) -> str:
        if v not in VALID_GOALS:
            raise ValueError(f"investment_goal must be one of {sorted(VALID_GOALS)}")
        return v
