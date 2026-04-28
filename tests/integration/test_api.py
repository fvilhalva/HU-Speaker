"""Testes de integração da API."""

from fastapi.testclient import TestClient # type: ignore[import]
 
from hu_speaker.main import app # type: ignore[import]


def test_root_endpoint() -> None:
    """Testa o endpoint raiz."""
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "HU-Speaker API online"}


def test_health_endpoint() -> None:
    """Testa o endpoint de health check."""
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_readiness_endpoint() -> None:
    """Testa o endpoint de prontidão."""
    client = TestClient(app)
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["ready"] is True


def test_favicon_endpoint() -> None:
    """Testa o endpoint de favicon."""
    client = TestClient(app)
    response = client.get("/favicon.ico")

    assert response.status_code == 204


def test_speaker_synthesize_endpoint() -> None:
    """Testa o endpoint de síntese."""
    client = TestClient(app)
    response = client.post(
        "/speak/synthesize",
        json={"text": "Olá", "language": "pt_BR"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Olá"
    assert data["language"] == "pt_BR"
    assert data["status"] == "processing"
    assert "id" in data


def test_speaker_status_endpoint() -> None:
    """Testa o endpoint de status de síntese."""
    client = TestClient(app)
    response = client.get("/speak/status/test-123")

    assert response.status_code == 200
    assert response.json()["id"] == "test-123"
    assert response.json()["status"] == "completed"
