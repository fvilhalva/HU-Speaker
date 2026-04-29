"""Controller de Speaker (Síntese de Voz)."""

from hu_speaker.modules.speaker.schemas import SynthesisRequest, SynthesisResponse
from hu_speaker.modules.speaker.service import SpeakerService


class SpeakerController:
    """Controller para endpoints de síntese de voz."""

    def __init__(self, service: SpeakerService | None = None) -> None:
        """Inicializa o controller com o serviço de síntese."""
        self.service = service or SpeakerService()

    def synthesize(self, request: SynthesisRequest) -> SynthesisResponse:
        """Processa uma requisição de síntese de voz."""
        result = self.service.synthesize(
            text=request.text,
            language=request.language,
            length_scale=request.length_scale
        )

        return SynthesisResponse(**result)

    def get_status(self, synthesis_id: str) -> dict[str, str]:
        """Obtém o status de uma síntese."""
        return self.service.get_synthesis_status(synthesis_id)

    def get_audio(self, synthesis_id: str) -> bytes:
        """Obtém o arquivo WAV sintetizado."""
        audio_path = self.service.get_audio_file(synthesis_id)
        with open(audio_path, "rb") as f:
            return f.read()
