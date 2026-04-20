"""Tests for events endpoints."""
from unittest.mock import MagicMock


def test_get_events_returns_list(client, mock_supabase):
    mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
    response = client.get("/api/events/")
    assert response.status_code == 200


def test_get_events_with_limit(client, mock_supabase):
    mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
    response = client.get("/api/events/?limit=10")
    assert response.status_code == 200
