"""Router de Speaker (Síntese de Voz)."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from hu_speaker.core.security import AuthContext, require_service_jwt
from hu_speaker.modules.speaker.controller import SpeakerController
from hu_speaker.modules.speaker.schemas import DeletionResponse, SynthesisRequest, SynthesisResponse

router = APIRouter(prefix="/speak", tags=["speaker"])
speaker_controller = SpeakerController()
logger = logging.getLogger(__name__)


@router.post("/synthesize", response_model=SynthesisResponse)
def synthesize(
    request: SynthesisRequest, auth: AuthContext = Depends(require_service_jwt)
) -> SynthesisResponse:
    """Sintetiza um texto em áudio."""
    logger.info(
        "Synthesis requested",
        extra={
            "subject": auth.subject,
            "source_system": auth.source_system,
            "actor_id": auth.actor_id,
            "actor_name": auth.actor_name,
            "actor_role": auth.actor_role,
            "request_id": auth.request_id,
        },
    )
    return speaker_controller.synthesize(request)


@router.get("/status/{synthesis_id}", response_model=dict[str, str])
def get_synthesis_status(
    synthesis_id: str, auth: AuthContext = Depends(require_service_jwt)
) -> dict[str, str]:
    """Obtém o status de uma síntese."""
    logger.info(
        "Status check",
        extra={
            "synthesis_id": synthesis_id,
            "subject": auth.subject,
            "source_system": auth.source_system,
        },
    )
    return speaker_controller.get_status(synthesis_id)


@router.get("/download/{synthesis_id}")
def download_audio(
    synthesis_id: str, auth: AuthContext = Depends(require_service_jwt)
) -> FileResponse:
    """Baixa o arquivo WAV sintetizado."""
    try:
        audio_path = speaker_controller.service.get_audio_file(synthesis_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    logger.info(
        "Audio download requested",
        extra={
            "synthesis_id": synthesis_id,
            "audio_path": str(audio_path),
            "subject": auth.subject,
            "actor_id": auth.actor_id,
        },
    )
    return FileResponse(
        path=audio_path,
        media_type="audio/wav",
        filename=f"{synthesis_id}.wav",
    )


@router.delete("/{synthesis_id}", response_model=DeletionResponse)
def delete_audio(
    synthesis_id: str, auth: AuthContext = Depends(require_service_jwt)
) -> DeletionResponse:
    """Exclui o arquivo WAV sintetizado e seus metadados."""
    try:
        speaker_controller.delete_audio(synthesis_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    logger.info(
        "Audio deletion requested",
        extra={
            "synthesis_id": synthesis_id,
            "subject": auth.subject,
            "actor_id": auth.actor_id,
            "actor_name": auth.actor_name,
        },
    )
    return DeletionResponse(
        id=synthesis_id,
        status="deleted",
        message="Audio deleted successfully",
    )
