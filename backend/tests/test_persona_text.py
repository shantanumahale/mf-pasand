"""Tests for persona_to_natural_text."""

from app.models.persona import UserPersona
from app.services.fund_text import persona_to_natural_text


def _full_persona() -> UserPersona:
    return UserPersona(
        age=30,
        annual_income=15.0,
        investment_horizon="long",
        risk_appetite="high",
        investment_goal="wealth_creation",
        monthly_sip_budget=10000,
        lumpsum_available=500000,
        existing_investments="PPF, FD worth 5 lakhs",
        preferences="Prefer large cap funds",
    )


class TestPersonaToNaturalText:
    def test_full_persona(self):
        text = persona_to_natural_text(_full_persona())
        assert "30-year-old" in text
        assert "15 lakhs" in text
        assert "long-term" in text
        assert "high risk" in text
        assert "wealth creation" in text
        assert "10,000" in text
        assert "500,000" in text  # lumpsum
        assert "PPF" in text
        assert "large cap" in text

    def test_minimal_persona(self):
        persona = UserPersona(
            age=25,
            investment_horizon="short",
            risk_appetite="low",
            investment_goal="emergency_fund",
        )
        text = persona_to_natural_text(persona)
        assert "25-year-old" in text
        assert "short-term" in text
        assert "low risk" in text
        assert "emergency" in text
        # None fields should not appear
        assert "None" not in text
        assert "lump" not in text.lower()

    def test_tax_saving_goal(self):
        persona = UserPersona(
            age=40,
            investment_horizon="medium",
            risk_appetite="moderate",
            investment_goal="tax_saving",
        )
        text = persona_to_natural_text(persona)
        assert "80C" in text or "tax" in text.lower()
