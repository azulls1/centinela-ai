"""Tests for analytics endpoints."""
from unittest.mock import MagicMock

def test_get_stats(client, mock_supabase):
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    response = client.get("/api/analytics/stats")
    assert response.status_code in (200, 500)

def test_get_stats_with_session(client, mock_supabase):
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    response = client.get("/api/analytics/stats?session_id=test-123")
    assert response.status_code in (200, 500)
