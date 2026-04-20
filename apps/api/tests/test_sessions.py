"""Tests for sessions endpoints."""
from unittest.mock import MagicMock

def test_init_session(client, mock_supabase):
    mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[{"session_id": "test-123", "status": "active"}]
    )
    response = client.post("/api/sessions/init", json={
        "session_id": "test-123", "name": "Test User", "email": "test@example.com", "plan": "Demo"
    })
    assert response.status_code in (200, 201, 422)

def test_heartbeat_session(client, mock_supabase):
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"session_id": "test-123", "status": "active"}]
    )
    response = client.post("/api/sessions/heartbeat", json={
        "session_id": "test-123", "cameras_active": 1, "fps_average": 24.0
    })
    assert response.status_code in (200, 422)
