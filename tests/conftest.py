import pytest
from unittest.mock import patch, MagicMock
from app import create_app

@pytest.fixture(scope='session')
def app():
    return create_app('testing')

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def mock_gemini():
    """Mock google-genai SDK."""
    with patch('services.gemini_service.genai') as m:
        client = MagicMock()
        m.Client.return_value = client
        resp = MagicMock()
        resp.text = 'Gate 2 is clear with 2 min wait.'
        client.models.generate_content.return_value = resp
        yield client

@pytest.fixture(autouse=True)
def mock_firebase():
    with patch('firebase_admin.auth') as m:
        m.verify_id_token.return_value = {'uid': 'test-123', 'staff': False}
        yield m
