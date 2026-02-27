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
    response = client.get("/hello")
    assert response.status_code == 200
    assert b"Hello, world!" in response.data


def test_home_page(client):
    """Test the home page returns 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_banner_route(client):
    """Test the banner route returns 200."""
    response = client.get("/banner")
    assert response.status_code == 200


def test_dropdowns_route(client):
    """Test the dropdowns route returns 200."""
    response = client.get("/dropdowns")
    assert response.status_code == 200


def test_info_route(client):
    """Test the info route returns 200."""
    response = client.get("/info")
    assert response.status_code == 200
