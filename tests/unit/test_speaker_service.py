"""Testes unitários do módulo de Speaker."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from hu_speaker.modules.speaker.service import SpeakerService


class FakeChunk:
    """Imita um AudioChunk do piper-tts 1.6.0 (bytes int16)."""

    def __init__(self, data: bytes) -> None:
        self.audio_int16_bytes = data


class FakeVoice:
    def synthesize(self, text: str, syn_config: object = None) -> Iterator[FakeChunk]:
        # 1s de silêncio PCM 16-bit mono @ 22050 Hz, em um único chunk.
        yield FakeChunk(b"\x00\x00" * 22050)


def test_speaker_service_synthesize(tmp_path: Path) -> None:
    """Testa a síntese de voz."""
    service = SpeakerService(voice=FakeVoice(), output_dir=tmp_path)
    result = service.synthesize(text="Olá, mundo", language="pt_BR")

    assert result["text"] == "Olá, mundo"
    assert result["language"] == "pt_BR"
    assert result["status"] == "completed"
    assert "id" in result
    assert (tmp_path / f"{result['id']}.wav").exists()


def test_speaker_service_get_status(tmp_path: Path) -> None:
    """Testa a obtenção de status de síntese."""
    service = SpeakerService(voice=FakeVoice(), output_dir=tmp_path)
    result = service.synthesize(text="Texto de teste", language="pt_BR")

    status = service.get_synthesis_status(synthesis_id=result["id"])

    assert status["id"] == result["id"]
    assert status["status"] == "completed"


def test_speaker_service_delete_audio(tmp_path: Path) -> None:
    """Testa a exclusão de um áudio sintetizado."""
    service = SpeakerService(voice=FakeVoice(), output_dir=tmp_path)
    result = service.synthesize(text="Texto de teste", language="pt_BR")

    audio_path = tmp_path / f"{result['id']}.wav"
    assert audio_path.exists()

    service.delete_audio_file(result["id"])

    assert not audio_path.exists()
