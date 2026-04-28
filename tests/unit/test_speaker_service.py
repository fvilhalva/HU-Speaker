"""Testes unitários do módulo de Speaker."""

from hu_speaker.modules.speaker.schemas import SynthesisRequest
from hu_speaker.modules.speaker.service import SpeakerService


def test_speaker_service_synthesize() -> None:
    """Testa a síntese de voz."""
    service = SpeakerService()
    result = service.synthesize(text="Olá, mundo", language="pt_BR")

    assert result["text"] == "Olá, mundo"
    assert result["language"] == "pt_BR"
    assert result["status"] == "processing"
    assert "id" in result


def test_speaker_service_get_status() -> None:
    """Testa a obtenção de status de síntese."""
    service = SpeakerService()
    result = service.get_synthesis_status(synthesis_id="test-id-123")

    assert result["id"] == "test-id-123"
    assert result["status"] == "completed"
