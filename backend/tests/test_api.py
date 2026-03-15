"""Basic API endpoint tests using FastAPI TestClient."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_degraded_when_es_down(self, client):
        """Health should return degraded when ES is not reachable."""
        with patch("app.main.get_es_client") as mock_es:
            mock_client = AsyncMock()
            mock_client.info.side_effect = ConnectionError("ES not available")
            mock_es.return_value = mock_client

            resp = client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "degraded"


class TestRecommendEndpoint:
    def test_invalid_persona_rejected(self, client):
        """Missing required fields should return 422."""
        resp = client.post("/recommend", json={"age": 15})
        assert resp.status_code == 422

    def test_invalid_age(self, client):
        resp = client.post(
            "/recommend",
            json={
                "age": 10,
                "investment_horizon": "long",
                "risk_appetite": "high",
                "investment_goal": "wealth_creation",
            },
        )
        assert resp.status_code == 422

    def test_invalid_risk_appetite(self, client):
        resp = client.post(
            "/recommend",
            json={
                "age": 30,
                "investment_horizon": "long",
                "risk_appetite": "extreme",
                "investment_goal": "wealth_creation",
            },
        )
        assert resp.status_code == 422


class TestFundsEndpoint:
    def test_fund_not_found(self, client):
        """GET /funds/999999 should return 502 or 404 depending on ES state."""
        # Without ES running, this will raise -- just verify the route exists
        with patch("app.api.routes.funds.get_es_client") as mock_es:
            mock_client = AsyncMock()
            mock_client.search.return_value = {"hits": {"hits": [], "total": {"value": 0}}}
            mock_es.return_value = mock_client

            resp = client.get("/funds/999999")
            assert resp.status_code == 404

    def test_list_funds_default(self, client):
        with patch("app.api.routes.funds.get_es_client") as mock_es:
            mock_client = AsyncMock()
            mock_client.search.return_value = {
                "hits": {
                    "hits": [],
                    "total": {"value": 0},
                }
            }
            mock_es.return_value = mock_client

            resp = client.get("/funds")
            assert resp.status_code == 200
            data = resp.json()
            assert data["total"] == 0
            assert data["page"] == 1
