"""Service de Speaker (Síntese de Voz)."""

from __future__ import annotations

import logging
import re
import uuid
import wave
from pathlib import Path
from typing import Any
# Coqui TTS
# from TTS.api import TTS
# pip install TTS
# from TTS.api import TTS
try:
    from piper import PiperVoice  # type: ignore[import]
    from piper.config import SynthesisConfig  # type: ignore[import]
except ImportError:  # pragma: no cover - depends on runtime environment
    PiperVoice = Any
    SynthesisConfig = Any

from hu_speaker.core.config import get_settings


logger = logging.getLogger(__name__)


class SpeakerService:
    """Serviço de síntese de voz usando Piper TTS."""

    # Mapa de dígitos para palavras em português
    DIGIT_MAP = {
        "0": "zero",
        "1": "um",
        "2": "dois",
        "3": "três",
        "4": "quatro",
        "5": "cinco",
        "6": "seis",
        "7": "sete",
        "8": "oito",
        "9": "nove",
    }

    def __init__(
        self,
        voice: Any | None = None,
        model_path: Path | None = None,
        output_dir: Path | None = None,
    ) -> None:
        settings = get_settings()
        package_dir = Path(__file__).resolve().parents[2]

        self.model_path = model_path or (package_dir / "models" / settings.PIPER_MODEL)
        self.output_dir = output_dir or Path(settings.AUDIO_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._voice = voice
        self._syntheses: dict[str, dict[str, str]] = {}

    def _get_voice(self) -> Any:
        if self._voice is None:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Piper model not found: {self.model_path}")

            self._voice = PiperVoice.load(str(self.model_path))

        return self._voice

    @staticmethod
    def _preprocess_text(text: str) -> str:
        """Pré-processa o texto para melhor pronúncia.
        
        Converte sequências de caracteres isolados em palavras soltas.
        Exemplo: "A1234" → "A um dois três quatro"
        
        Args:
            text: Texto original
        
        Returns:
            Texto pré-processado
        """
        # Substituir dígitos por palavras
        result = text
        for digit, word in SpeakerService.DIGIT_MAP.items():
            # Substituir dígito isolado (cercado por não-alfanuméricos ou fim de string)
            # Mas manter números que são parte de palavras
            result = re.sub(r"(?<![a-zA-Z0-9])" + digit + r"(?![a-zA-Z0-9])", f" {word} ", result)
        
        # Limpar múltiplos espaços
        result = re.sub(r"\s+", " ", result).strip()
        
        return result

    def synthesize(self, text: str, language: str = "pt_BR", length_scale: float = 1.0) -> dict[str, str]:
        """Sintetiza um texto em áudio.
        
        Args:
            text: Texto a sintetizar
            language: Idioma (padrão: pt_BR)
            length_scale: Velocidade do áudio (0.5-2.0, padrão 1.0)
        """
        text = text.strip()
        if not text:
            raise ValueError("text must not be empty")

        # Pré-processar para melhor pronúncia
        processed_text = self._preprocess_text(text)

        synthesis_id = str(uuid.uuid4())
        audio_path = self.output_dir / f"{synthesis_id}.wav"

        voice = self._get_voice()
        with wave.open(str(audio_path), "wb") as wav_file:
            # Use synthesize_wav() which handles WAV format setup automatically
            syn_config = SynthesisConfig(length_scale=length_scale) if length_scale != 1.0 else None
            voice.synthesize_wav(processed_text, wav_file, syn_config=syn_config)

        result = {
            "id": synthesis_id,
            "text": text,  # Retorna o texto original no resultado
            "language": language,
            "status": "completed",
        }

        self._syntheses[synthesis_id] = {**result, "audio_path": str(audio_path)}
        logger.info("Audio synthesized", extra={"synthesis_id": synthesis_id, "audio_path": str(audio_path)})
        return result

    def get_synthesis_status(self, synthesis_id: str) -> dict[str, str]:
        """Obtém o status de uma síntese em andamento."""
        synthesis = self._syntheses.get(synthesis_id)
        if synthesis is None:
            return {"id": synthesis_id, "status": "completed"}

        return {"id": synthesis["id"], "status": synthesis["status"]}

    def get_audio_file(self, synthesis_id: str) -> Path:
        """Retorna o caminho do arquivo WAV sintetizado."""
        audio_path = self.output_dir / f"{synthesis_id}.wav"
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        return audio_path

    def delete_audio_file(self, synthesis_id: str) -> None:
        """Remove o arquivo WAV e os metadados associados."""
        audio_path = self.output_dir / f"{synthesis_id}.wav"
        if not audio_path.exists() and synthesis_id not in self._syntheses:
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if audio_path.exists():
            audio_path.unlink()

        self._syntheses.pop(synthesis_id, None)
        logger.info("Audio deleted", extra={"synthesis_id": synthesis_id, "audio_path": str(audio_path)})

