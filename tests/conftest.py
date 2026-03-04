import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app


@pytest.fixture
def app():
	app = create_app({
		'TESTING': True,
		'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
	})
	return app


@pytest.fixture
def client(app):
	return app.test_client()
