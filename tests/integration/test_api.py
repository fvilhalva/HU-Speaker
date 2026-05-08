"""Testes de integração da API."""

from __future__ import annotations

import wave
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest
import jwt
from fastapi.testclient import TestClient  # type: ignore[import]

from hu_speaker.main import app  # type: ignore[import]
from hu_speaker.modules.speaker import router as speaker_router
from hu_speaker.modules.speaker.controller import SpeakerController
from hu_speaker.modules.speaker.service import SpeakerService


class FakeVoice:
    def synthesize_wav(self, text: str, wav_file: wave.Wave_write, syn_config=None) -> None:
        wav_file.setframerate(22050)
        wav_file.setsampwidth(2)
        wav_file.setnchannels(1)
        wav_file.writeframes(b"\x00\x00" * 22050)


@pytest.fixture()
def speaker_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    from hu_speaker.core import config as config_module

    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret")
    config_module.get_settings.cache_clear()
    service = SpeakerService(voice=FakeVoice(), output_dir=tmp_path)
    monkeypatch.setattr(speaker_router, "speaker_controller", SpeakerController(service))
    return TestClient(app)


def auth_headers() -> dict[str, str]:
    payload = {
        "sub": "novosga-service",
        "source_system": "novosga",
        "actor_id": "123",
        "actor_name": "Maria Silva",
        "actor_role": "attendant",
        "request_id": "req-001",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }
    token = jwt.encode(payload, "test-jwt-secret", algorithm="HS256")
    return {
        "Authorization": f"Bearer {token}",
    }


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


def test_speaker_synthesize_endpoint(speaker_client: TestClient) -> None:
    """Testa o endpoint de síntese."""
    response = speaker_client.post(
        "/speak/synthesize",
        headers=auth_headers(),
        json={"text": "Olá", "language": "pt_BR"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Olá"
    assert data["language"] == "pt_BR"
    assert data["status"] == "completed"
    assert "id" in data


def test_speaker_status_endpoint(speaker_client: TestClient) -> None:
    """Testa o endpoint de status de síntese."""
    response = speaker_client.get("/speak/status/test-123", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["id"] == "test-123"
    assert response.json()["status"] == "completed"


def test_speaker_delete_endpoint(speaker_client: TestClient) -> None:
    """Testa o endpoint de exclusão de áudio."""
    synthesis_response = speaker_client.post(
        "/speak/synthesize",
        headers=auth_headers(),
        json={"text": "Excluir depois", "language": "pt_BR"},
    )

    synthesis_id = synthesis_response.json()["id"]
    response = speaker_client.delete(f"/speak/{synthesis_id}", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["id"] == synthesis_id
    assert response.json()["status"] == "deleted"


def test_speaker_requires_api_key(speaker_client: TestClient) -> None:
    """Testa bloqueio sem token JWT."""
    response = speaker_client.post(
        "/speak/synthesize",
        json={"text": "Sem auth", "language": "pt_BR"},
    )

    assert response.status_code == 401
