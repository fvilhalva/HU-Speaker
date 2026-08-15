"""Service de Speaker (Síntese de Voz)."""

from __future__ import annotations

import logging
import re
import uuid
import wave
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
    def _spell_digits(digits: str) -> str:
        """Soletra uma sequência de dígitos: '007' -> 'zero zero sete'."""
        return " ".join(SpeakerService.DIGIT_MAP[c] for c in digits)

    @staticmethod
    def _preprocess_text(text: str) -> str:
        """Pré-processa o texto para melhor pronúncia pelo Piper.

        O Piper tropeça em "tokens" que misturam letra e número colados
        (ex.: uma senha "A001"), chegando a engolir a letra. Aqui esses
        casos são separados e os dígitos são soletrados um a um.

        Exemplos:
            "Senha A001"            -> "Senha A zero zero um"
            "Senha C007, sala 12"   -> "Senha C zero zero sete, sala um dois"
            "guichê 03"             -> "guichê zero três"

        Args:
            text: Texto original

        Returns:
            Texto pré-processado, pronto para a síntese
        """
        # 1) Token de senha: uma ou mais letras seguidas de dígitos (ex.: "A001").
        #    Mantém a(s) letra(s) e soletra os dígitos separadamente.
        def _repl_senha(m: re.Match[str]) -> str:
            letras, numeros = m.group(1), m.group(2)
            return f"{letras} {SpeakerService._spell_digits(numeros)}"

        result = re.sub(r"\b([A-Za-z]+)(\d+)\b", _repl_senha, text)

        # 2) Números soltos restantes (ex.: o "03" de "guichê 03") também são
        #    soletrados dígito a dígito, para pronúncia clara em painel.
        result = re.sub(r"\d+", lambda m: SpeakerService._spell_digits(m.group(0)), result)

        # 3) Normaliza espaços em excesso.
        result = re.sub(r"\s+", " ", result).strip()

        return result

    def synthesize(
        self, text: str, language: str = "pt_BR", length_scale: float = 1.0
    ) -> dict[str, str]:
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
        syn_config = SynthesisConfig(length_scale=length_scale) if length_scale != 1.0 else None

        # Sample rate do modelo (pt_BR faber = 22050 Hz).
        try:
            sample_rate = int(voice.config.sample_rate)
        except AttributeError:
            sample_rate = 22050

        # piper-tts 1.6.0: voice.synthesize() devolve uma sequencia de AudioChunk.
        # Concatena os bytes int16 de TODOS os chunks e grava um unico WAV com o
        # cabecalho correto. (Escrever apenas o primeiro chunk cortava a fala e
        # deixava o audio truncado/estranho.)
        audio_bytes = bytearray()
        for chunk in voice.synthesize(processed_text, syn_config=syn_config):
            data = getattr(chunk, "audio_int16_bytes", None)
            if data is None:
                # fallbacks para variacoes de atributo entre versoes
                data = getattr(chunk, "audio_int16", None)
                if data is not None and not isinstance(data, (bytes, bytearray)):
                    data = data.tobytes()
            if data:
                audio_bytes.extend(data)

        with wave.open(str(audio_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit PCM
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(bytes(audio_bytes))

        result = {
            "id": synthesis_id,
            "text": text,  # Retorna o texto original no resultado
            "language": language,
            "status": "completed",
        }

        self._syntheses[synthesis_id] = {**result, "audio_path": str(audio_path)}
        logger.info(
            "Audio synthesized",
            extra={"synthesis_id": synthesis_id, "audio_path": str(audio_path)},
        )
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
        logger.info(
            "Audio deleted",
            extra={"synthesis_id": synthesis_id, "audio_path": str(audio_path)},
        )