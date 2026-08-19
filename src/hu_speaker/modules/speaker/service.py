"""Service de Speaker (Síntese de Voz).

Orquestra a síntese: pré-processa o texto, escolhe a *engine* de TTS
(Piper, Kokoro, ...) conforme o modelo pedido, grava o WAV e mantém os
metadados. O que é específico de cada motor vive em ``engines/``.
"""

from __future__ import annotations

import logging
import re
import uuid
import wave
from pathlib import Path
from typing import Any

from hu_speaker.core.config import get_settings
from hu_speaker.core.exceptions import UnknownModelError
from hu_speaker.modules.speaker.engines import (
    AVAILABLE_MODELS,
    KokoroEngine,
    PiperEngine,
    TTSEngine,
)

logger = logging.getLogger(__name__)


class SpeakerService:
    """Serviço de síntese de voz com múltiplas engines de TTS."""

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

        self._default_model = settings.DEFAULT_TTS_MODEL.lower()
        # Voz Piper injetada (usada nos testes). Encaminhada à PiperEngine.
        self._injected_voice = voice
        # Cache de engines já instanciadas (carregar modelo é caro).
        self._engines: dict[str, TTSEngine] = {}
        self._syntheses: dict[str, dict[str, str]] = {}

    def _build_engine(self, model: str) -> TTSEngine:
        settings = get_settings()
        if model == PiperEngine.name:
            return PiperEngine(self.model_path, voice=self._injected_voice)
        if model == KokoroEngine.name:
            return KokoroEngine(
                lang_code=settings.KOKORO_LANG_CODE,
                voice=settings.KOKORO_VOICE,
            )
        raise UnknownModelError(model, AVAILABLE_MODELS)

    def _get_engine(self, model: str) -> TTSEngine:
        model = (model or self._default_model).lower()
        if model not in AVAILABLE_MODELS:
            raise UnknownModelError(model, AVAILABLE_MODELS)
        if model not in self._engines:
            self._engines[model] = self._build_engine(model)
        return self._engines[model]

    @staticmethod
    def _spell_digits(digits: str) -> str:
        """Soletra uma sequência de dígitos: '007' -> 'zero zero sete'."""
        return " ".join(SpeakerService.DIGIT_MAP[c] for c in digits)

    @staticmethod
    def _preprocess_text(text: str) -> str:
        """Pré-processa o texto para melhor pronúncia pela engine.

        As engines tropeçam em "tokens" que misturam letra e número colados
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

    def _synthesize_pcm(
        self, model: str, processed_text: str, length_scale: float
    ) -> tuple[bytes, int, str]:
        """Sintetiza usando ``model``, com fallback para o Piper em caso de falha.

        Returns:
            ``(pcm_bytes, sample_rate, used_model)`` — ``used_model`` reflete a
            engine que de fato produziu o áudio (pode diferir de ``model`` se o
            fallback for acionado).
        """
        engine = self._get_engine(model)
        try:
            pcm, sample_rate = engine.synthesize_pcm(processed_text, length_scale)
            return pcm, sample_rate, engine.name
        except Exception as exc:  # noqa: BLE001 - fallback resiliente por design
            if engine.name == PiperEngine.name:
                # Piper é o motor base; se ele falhar não há para onde cair.
                raise
            logger.warning(
                "TTS engine failed, falling back to Piper",
                extra={"model": engine.name, "error": str(exc)},
            )
            fallback = self._get_engine(PiperEngine.name)
            pcm, sample_rate = fallback.synthesize_pcm(processed_text, length_scale)
            return pcm, sample_rate, fallback.name

    def synthesize(
        self,
        text: str,
        language: str = "pt_BR",
        length_scale: float = 1.0,
        model: str | None = None,
    ) -> dict[str, str]:
        """Sintetiza um texto em áudio.

        Args:
            text: Texto a sintetizar
            language: Idioma (padrão: pt_BR)
            length_scale: Velocidade do áudio (0.5-2.0, padrão 1.0). Maior =
                mais devagar.
            model: Modelo de voz ("piper", "kokoro"). Se ``None``, usa o
                ``DEFAULT_TTS_MODEL`` das configurações.
        """
        text = text.strip()
        if not text:
            raise ValueError("text must not be empty")

        # Pré-processar para melhor pronúncia
        processed_text = self._preprocess_text(text)

        synthesis_id = str(uuid.uuid4())
        audio_path = self.output_dir / f"{synthesis_id}.wav"

        requested_model = (model or self._default_model).lower()
        audio_bytes, sample_rate, used_model = self._synthesize_pcm(
            requested_model, processed_text, length_scale
        )

        with wave.open(str(audio_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit PCM
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_bytes)

        result = {
            "id": synthesis_id,
            "text": text,  # Retorna o texto original no resultado
            "language": language,
            "model": used_model,
            "status": "completed",
        }

        self._syntheses[synthesis_id] = {**result, "audio_path": str(audio_path)}
        logger.info(
            "Audio synthesized",
            extra={
                "synthesis_id": synthesis_id,
                "audio_path": str(audio_path),
                "requested_model": requested_model,
                "used_model": used_model,
            },
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
