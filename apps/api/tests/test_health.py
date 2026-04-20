"""Tests for health and root endpoints."""
from unittest.mock import MagicMock


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["version"] == "1.0.0"


def test_api_info(client):
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "features" in data
    assert "endpoints" in data


def test_health_check(client, mock_supabase):
    mock_supabase.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock(data=[{"id": 1}])
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
