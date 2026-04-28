"""Router de Speaker (Síntese de Voz)."""

from fastapi import APIRouter

from hu_speaker.modules.speaker.controller import SpeakerController
from hu_speaker.modules.speaker.schemas import SynthesisRequest, SynthesisResponse

router = APIRouter(prefix="/speak", tags=["speaker"])
speaker_controller = SpeakerController()


@router.post("/synthesize", response_model=SynthesisResponse)
def synthesize(request: SynthesisRequest) -> SynthesisResponse:
    """Sintetiza um texto em áudio."""
    return speaker_controller.synthesize(request)


@router.get("/status/{synthesis_id}", response_model=dict[str, str])
def get_synthesis_status(synthesis_id: str) -> dict[str, str]:
    """Obtém o status de uma síntese."""
    return speaker_controller.get_status(synthesis_id)
