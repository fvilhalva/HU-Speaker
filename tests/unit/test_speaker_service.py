"""Testes unitários do módulo de Speaker."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from hu_speaker.core.exceptions import UnknownModelError
from hu_speaker.modules.speaker.engines.base import TTSEngine
from hu_speaker.modules.speaker.service import SpeakerService


class FakeChunk:
    """Imita um AudioChunk do piper-tts 1.6.0 (bytes int16)."""

    def __init__(self, data: bytes) -> None:
        self.audio_int16_bytes = data


class FakeVoice:
    def synthesize(self, text: str, syn_config: object = None) -> Iterator[FakeChunk]:
        # 1s de silêncio PCM 16-bit mono @ 22050 Hz, em um único chunk.
        yield FakeChunk(b"\x00\x00" * 22050)


class FakeEngine(TTSEngine):
    """Engine de teste que devolve silêncio (ou falha, se configurada)."""

    def __init__(self, name: str, *, fail: bool = False) -> None:
        self.name = name
        self._fail = fail

    def synthesize_pcm(self, text: str, length_scale: float = 1.0) -> tuple[bytes, int]:
        if self._fail:
            raise RuntimeError("engine indisponível")
        return b"\x00\x00" * 24000, 24000


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


def test_synthesize_reports_used_model(tmp_path: Path) -> None:
    """A síntese informa qual modelo foi efetivamente usado (padrão: piper)."""
    service = SpeakerService(voice=FakeVoice(), output_dir=tmp_path)
    result = service.synthesize(text="Olá", language="pt_BR")

    assert result["model"] == "piper"


def test_synthesize_selects_requested_model(tmp_path: Path) -> None:
    """O modelo pedido no argumento é o que sintetiza."""
    service = SpeakerService(voice=FakeVoice(), output_dir=tmp_path)
    # injeta uma engine kokoro fake no cache (evita carregar o modelo real)
    service._engines["kokoro"] = FakeEngine("kokoro")

    result = service.synthesize(text="João", model="kokoro")

    assert result["model"] == "kokoro"


def test_synthesize_unknown_model_raises(tmp_path: Path) -> None:
    """Modelo inexistente vira erro de API (400)."""
    service = SpeakerService(voice=FakeVoice(), output_dir=tmp_path)

    with pytest.raises(UnknownModelError):
        service.synthesize(text="João", model="inexistente")


def test_synthesize_falls_back_to_piper_on_engine_failure(tmp_path: Path) -> None:
    """Se a engine escolhida falha, cai para o Piper e reporta 'piper'."""
    service = SpeakerService(voice=FakeVoice(), output_dir=tmp_path)
    service._engines["kokoro"] = FakeEngine("kokoro", fail=True)

    result = service.synthesize(text="João", model="kokoro")

    assert result["model"] == "piper"
    assert (tmp_path / f"{result['id']}.wav").exists()
