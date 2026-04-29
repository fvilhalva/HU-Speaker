"""Testes unitários do módulo de Speaker."""

from __future__ import annotations

import wave
from pathlib import Path

from hu_speaker.modules.speaker.service import SpeakerService


class FakeVoice:
    def synthesize(self, text: str, wav_file: wave.Wave_write) -> None:
        wav_file.setframerate(22050)
        wav_file.setsampwidth(2)
        wav_file.setnchannels(1)
        wav_file.writeframes(b"\x00\x00" * 22050)


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
