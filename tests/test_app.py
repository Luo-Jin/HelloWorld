import pytest
from app import create_app


@pytest.fixture
def app():
    """Create test app."""
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_hello_route(client):
    """Test the hello route returns 200 and correct message."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello, world!" in response.data
