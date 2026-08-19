"""Engine de síntese baseada no Kokoro TTS.

Kokoro (https://github.com/hexgrad/kokoro) é um modelo pequeno (~82M) sob
licença Apache-2.0, com qualidade acima do Piper e capaz de rodar em CPU.
Suporte a português do Brasil via ``lang_code='p'``.

As dependências pesadas (``kokoro``, ``torch``, ``numpy``) são importadas de
forma preguiçosa, dentro dos métodos, para que o serviço suba normalmente
mesmo quando só o Piper está instalado.
"""

from __future__ import annotations

from typing import Any

from hu_speaker.modules.speaker.engines.base import TTSEngine

#: Sample rate fixo do Kokoro.
_SAMPLE_RATE = 24000


class KokoroEngine(TTSEngine):
    """Motor de maior qualidade (Apache-2.0), roda em CPU."""

    name = "kokoro"

    def __init__(self, lang_code: str = "p", voice: str = "pf_dora") -> None:
        """Cria a engine.

        Args:
            lang_code: Código de idioma do Kokoro (``'p'`` = português BR).
            voice: Nome da voz Kokoro (ex.: ``pf_dora``, ``pm_alex``).
        """
        self.lang_code = lang_code
        self.voice = voice
        self._pipeline: Any | None = None

    def _get_pipeline(self) -> Any:
        if self._pipeline is None:
            from kokoro import KPipeline  # import preguiçoso (dependência pesada)

            self._pipeline = KPipeline(lang_code=self.lang_code)
        return self._pipeline

    def synthesize_pcm(self, text: str, length_scale: float = 1.0) -> tuple[bytes, int]:
        import numpy as np

        pipeline = self._get_pipeline()

        # Piper: length_scale maior = mais devagar. Kokoro: speed menor = mais
        # devagar. Invertemos para manter a mesma semântica na API pública.
        speed = 1.0 / length_scale if length_scale else 1.0

        chunks: list[Any] = []
        for _graphemes, _phonemes, audio in pipeline(text, voice=self.voice, speed=speed):
            if audio is None:
                continue
            # audio pode vir como tensor torch ou array numpy (float32 em [-1, 1]).
            if hasattr(audio, "detach"):
                audio = audio.detach().cpu().numpy()
            chunks.append(np.asarray(audio, dtype=np.float32))

        if not chunks:
            return b"", _SAMPLE_RATE

        samples = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
        pcm = (np.clip(samples, -1.0, 1.0) * 32767.0).astype("<i2").tobytes()
        return pcm, _SAMPLE_RATE
