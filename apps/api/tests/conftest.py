import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    with patch("supabase_client.get_supabase_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def client(mock_supabase):
    """Create a test client with mocked Supabase."""
    from main import app
    return TestClient(app)
