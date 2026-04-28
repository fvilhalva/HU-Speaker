"""Configurações e fixtures para testes."""

import pytest
from fastapi.testclient import TestClient

from hu_speaker.main import app


@pytest.fixture
def client() -> TestClient:
    """Fixture para cliente de testes da API."""
    return TestClient(app)
