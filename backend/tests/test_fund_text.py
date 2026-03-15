"""Tests for fund_to_natural_text."""

from app.services.fund_text import fund_to_natural_text


def _complete_fund() -> dict:
    return {
        "scheme_name": "Axis Bluechip Fund Direct Growth",
        "fund_house": "Axis Mutual Fund",
        "category": "Large Cap",
        "fund_type": "Equity",
        "crisil_rating": "Very High",
        "expense_ratio": 0.45,
        "aum_cr": 32000.0,
        "returns_1y": 12.5,
        "returns_3y": 14.2,
        "returns_5y": 16.8,
        "volatility_1y": 15.3,
        "max_drawdown_1y": 8.7,
        "min_sip": 500.0,
        "min_lumpsum": 5000.0,
        "fund_manager": "Shreyash Devalkar",
    }


class TestFundToNaturalText:
    def test_complete_data(self):
        text = fund_to_natural_text(_complete_fund())
        assert "Axis Bluechip Fund Direct Growth" in text
        assert "Axis Mutual Fund" in text
        assert "Large Cap" in text
        assert "Equity" in text
        assert "very low" in text  # expense ratio interpretation
        assert "32,000" in text  # AUM
        assert "12.50%" in text  # 1Y return
        assert "Shreyash Devalkar" in text
        assert "500" in text  # min SIP
        assert "5,000" in text  # min lumpsum

    def test_missing_fields(self):
        """Only scheme_name provided; nothing should crash."""
        fund = {"scheme_name": "Test Fund"}
        text = fund_to_natural_text(fund)
        assert "Test Fund" in text
        assert "None" not in text

    def test_empty_dict(self):
        text = fund_to_natural_text({})
        # Should return something without raising
        assert isinstance(text, str)

    def test_missing_returns(self):
        fund = _complete_fund()
        del fund["returns_3y"]
        del fund["returns_5y"]
        text = fund_to_natural_text(fund)
        assert "12.50%" in text
        assert "three years" not in text
        assert "five years" not in text

    def test_only_sip(self):
        fund = {"scheme_name": "SIP Only Fund", "min_sip": 100.0}
        text = fund_to_natural_text(fund)
        assert "100" in text
        assert "lump" not in text.lower() or "lump-sum" not in text

    def test_only_lumpsum(self):
        fund = {"scheme_name": "Lump Fund", "min_lumpsum": 10000.0}
        text = fund_to_natural_text(fund)
        assert "10,000" in text

    def test_high_expense_ratio(self):
        fund = {"scheme_name": "Expensive Fund", "expense_ratio": 2.5}
        text = fund_to_natural_text(fund)
        assert "high" in text
