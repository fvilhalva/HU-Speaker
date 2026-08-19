"""Contrato comum das engines de síntese de voz (TTS).

Cada engine (Piper, Kokoro, ...) sabe apenas transformar *texto já
pré-processado* em PCM 16-bit mono. Todo o resto — pré-processamento do
texto, gravação do WAV, IDs, status, limpeza — vive no ``SpeakerService`` e
é compartilhado entre as engines. Assim, adicionar um novo motor é só criar
uma nova subclasse desta aqui.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class TTSEngine(ABC):
    """Interface comum a todas as engines de TTS."""

    #: Nome curto e estável usado no JSON (`{"model": "..."}`) e no registry.
    name: str = "base"

    @abstractmethod
    def synthesize_pcm(self, text: str, length_scale: float = 1.0) -> tuple[bytes, int]:
        """Sintetiza ``text`` e devolve o áudio cru.

        Args:
            text: Texto já pré-processado (dígitos soletrados etc.).
            length_scale: Velocidade da fala no padrão do Piper — **maior =
                mais devagar** (0.5 rápido … 2.0 bem devagar). Cada engine
                converte esse valor para a sua própria convenção.

        Returns:
            Uma tupla ``(pcm_bytes, sample_rate)`` onde ``pcm_bytes`` é áudio
            PCM 16-bit *little-endian*, mono, e ``sample_rate`` está em Hz.
        """
        raise NotImplementedError
