"""Engines de síntese de voz (TTS) disponíveis no HU-Speaker."""

from __future__ import annotations

from hu_speaker.modules.speaker.engines.base import TTSEngine
from hu_speaker.modules.speaker.engines.kokoro_engine import KokoroEngine
from hu_speaker.modules.speaker.engines.piper_engine import PiperEngine

#: Modelos que a API aceita no campo ``model`` do JSON de síntese.
AVAILABLE_MODELS: tuple[str, ...] = (PiperEngine.name, KokoroEngine.name)

__all__ = ["AVAILABLE_MODELS", "KokoroEngine", "PiperEngine", "TTSEngine"]
