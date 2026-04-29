"""Service de Speaker (Síntese de Voz)."""

from __future__ import annotations

import uuid
import wave
from pathlib import Path
from typing import Any

try:
    from piper import PiperVoice  # type: ignore[import]
    from piper.config import SynthesisConfig  # type: ignore[import]
except ImportError:  # pragma: no cover - depends on runtime environment
    PiperVoice = Any
    SynthesisConfig = Any

from hu_speaker.core.config import get_settings


class SpeakerService:
    """Serviço de síntese de voz usando Piper TTS."""

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

        synthesis_id = str(uuid.uuid4())
        audio_path = self.output_dir / f"{synthesis_id}.wav"

        voice = self._get_voice()
        with wave.open(str(audio_path), "wb") as wav_file:
            # Use synthesize_wav() which handles WAV format setup automatically
            syn_config = SynthesisConfig(length_scale=length_scale) if length_scale != 1.0 else None
            voice.synthesize_wav(text, wav_file, syn_config=syn_config)

        result = {
            "id": synthesis_id,
            "text": text,
            "language": language,
            "status": "completed",
        }

        self._syntheses[synthesis_id] = {**result, "audio_path": str(audio_path)}
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
