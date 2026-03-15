"""Tests for Elasticsearch query builders."""

from app.models.persona import UserPersona
from app.services.search import build_fund_list_query, build_recommendation_query


def _dummy_embedding(dims: int = 10) -> list[float]:
    return [0.1] * dims


class TestBuildRecommendationQuery:
    def test_basic_query(self):
        persona = UserPersona(
            age=30,
            investment_horizon="long",
            risk_appetite="high",
            investment_goal="wealth_creation",
        )
        query = build_recommendation_query(_dummy_embedding(), persona, top_k=20)

        assert "knn" in query
        assert query["knn"]["field"] == "fund_embedding"
        assert query["knn"]["k"] == 20
        assert query["size"] == 20
        # No filters for high risk / wealth_creation
        assert "filter" not in query["knn"]

    def test_low_risk_filter(self):
        persona = UserPersona(
            age=55,
            investment_horizon="short",
            risk_appetite="low",
            investment_goal="regular_income",
        )
        query = build_recommendation_query(_dummy_embedding(), persona)

        filters = query["knn"]["filter"]["bool"]["must"]
        rating_filter = next(
            (f for f in filters if "terms" in f and "crisil_rating.keyword" in f["terms"]),
            None,
        )
        assert rating_filter is not None
        assert "Low" in rating_filter["terms"]["crisil_rating.keyword"]

    def test_tax_saving_filter(self):
        persona = UserPersona(
            age=35,
            investment_horizon="long",
            risk_appetite="moderate",
            investment_goal="tax_saving",
        )
        query = build_recommendation_query(_dummy_embedding(), persona)
        filters = query["knn"]["filter"]["bool"]["must"]

        elss_filter = next(
            (f for f in filters if "term" in f and "category.keyword" in f["term"]),
            None,
        )
        assert elss_filter is not None
        assert elss_filter["term"]["category.keyword"] == "ELSS"

    def test_emergency_fund_filters(self):
        persona = UserPersona(
            age=28,
            investment_horizon="short",
            risk_appetite="low",
            investment_goal="emergency_fund",
        )
        query = build_recommendation_query(_dummy_embedding(), persona)
        filters = query["knn"]["filter"]["bool"]["must"]

        # Should have fund_type Debt filter
        debt_filter = next(
            (f for f in filters if "term" in f and "fund_type.keyword" in f.get("term", {})),
            None,
        )
        assert debt_filter is not None
        assert debt_filter["term"]["fund_type.keyword"] == "Debt"

        # Should have category filter for liquid-like categories
        cat_filter = next(
            (f for f in filters if "terms" in f and "category.keyword" in f["terms"]),
            None,
        )
        assert cat_filter is not None

    def test_sip_budget_filter(self):
        persona = UserPersona(
            age=25,
            investment_horizon="long",
            risk_appetite="high",
            investment_goal="wealth_creation",
            monthly_sip_budget=500,
        )
        query = build_recommendation_query(_dummy_embedding(), persona)
        filters = query["knn"]["filter"]["bool"]["must"]

        sip_filter = next(
            (f for f in filters if "range" in f and "min_sip" in f["range"]),
            None,
        )
        assert sip_filter is not None
        assert sip_filter["range"]["min_sip"]["lte"] == 500

    def test_lumpsum_filter(self):
        persona = UserPersona(
            age=40,
            investment_horizon="medium",
            risk_appetite="moderate",
            investment_goal="wealth_creation",
            lumpsum_available=100000,
        )
        query = build_recommendation_query(_dummy_embedding(), persona)
        filters = query["knn"]["filter"]["bool"]["must"]

        lump_filter = next(
            (f for f in filters if "range" in f and "min_lumpsum" in f["range"]),
            None,
        )
        assert lump_filter is not None
        assert lump_filter["range"]["min_lumpsum"]["lte"] == 100000


class TestBuildFundListQuery:
    def test_no_filters(self):
        query = build_fund_list_query(page=1, page_size=20)
        assert query["from"] == 0
        assert query["size"] == 20
        assert "match_all" in query["query"]

    def test_with_category_filter(self):
        query = build_fund_list_query(category="Large Cap", page=2, page_size=10)
        assert query["from"] == 10
        assert query["size"] == 10
        filters = query["query"]["bool"]["must"]
        assert any("category.keyword" in str(f) for f in filters)

    def test_pagination(self):
        query = build_fund_list_query(page=5, page_size=25)
        assert query["from"] == 100
        assert query["size"] == 25
