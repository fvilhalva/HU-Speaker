"""Engine de síntese baseada no Piper TTS."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from piper import PiperVoice
    from piper.config import SynthesisConfig
else:
    try:
        from piper import PiperVoice
        from piper.config import SynthesisConfig
    except ImportError:  # pragma: no cover - depends on runtime environment
        PiperVoice = Any
        SynthesisConfig = Any

from hu_speaker.modules.speaker.engines.base import TTSEngine

#: Sample rate do modelo pt_BR faber, usado como fallback.
_DEFAULT_SAMPLE_RATE = 22050


class PiperEngine(TTSEngine):
    """Motor rápido, leve e 100% CPU (voz padrão do projeto)."""

    name = "piper"

    def __init__(self, model_path: Path, voice: Any | None = None) -> None:
        """Cria a engine.

        Args:
            model_path: Caminho para o modelo ``.onnx``.
            voice: Voz Piper já carregada (usado nos testes para injetar um
                *fake*). Se ausente, é carregada sob demanda de ``model_path``.
        """
        self.model_path = model_path
        self._voice = voice

    def _get_voice(self) -> Any:
        if self._voice is None:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Piper model not found: {self.model_path}")
            self._voice = PiperVoice.load(str(self.model_path))
        return self._voice

    def synthesize_pcm(self, text: str, length_scale: float = 1.0) -> tuple[bytes, int]:
        voice = self._get_voice()
        syn_config = SynthesisConfig(length_scale=length_scale) if length_scale != 1.0 else None

        try:
            sample_rate = int(voice.config.sample_rate)
        except AttributeError:
            sample_rate = _DEFAULT_SAMPLE_RATE

        # piper-tts 1.6.0: voice.synthesize() devolve uma sequência de AudioChunk.
        # Concatena os bytes int16 de TODOS os chunks (escrever só o primeiro
        # truncava a fala).
        audio_bytes = bytearray()
        for chunk in voice.synthesize(text, syn_config=syn_config):
            data = getattr(chunk, "audio_int16_bytes", None)
            if data is None:
                # fallbacks para variações de atributo entre versões
                data = getattr(chunk, "audio_int16", None)
                if data is not None and not isinstance(data, (bytes, bytearray)):
                    data = data.tobytes()
            if data:
                audio_bytes.extend(data)

        return bytes(audio_bytes), sample_rate
