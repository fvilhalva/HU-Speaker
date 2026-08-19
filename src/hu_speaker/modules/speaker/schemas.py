"""Schemas (DTOs) para o módulo de Speaker."""

from pydantic import BaseModel, Field


class SynthesisRequest(BaseModel):
    """Requisição para síntese de voz."""

    text: str = Field(..., min_length=1, max_length=1000, description="Texto a ser sintetizado")
    language: str = Field(default="pt_BR", description="Idioma para síntese")
    length_scale: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Velocidade do áudio (0.5=rápido, 1.0=normal, 2.0=devagar)",
    )
    model: str | None = Field(
        default=None,
        description="Modelo de voz: 'piper' ou 'kokoro'. Ausente = padrão do servidor.",
    )


class SynthesisResponse(BaseModel):
    """Resposta da síntese de voz."""

    id: str = Field(..., description="ID único da requisição")
    text: str = Field(..., description="Texto sintetizado")
    language: str = Field(..., description="Idioma utilizado")
    model: str = Field(..., description="Modelo de voz efetivamente utilizado")
    status: str = Field(..., description="Status da síntese")


class DeletionResponse(BaseModel):
    """Resposta para exclusão de áudio."""

    id: str = Field(..., description="ID único do áudio")
    status: str = Field(..., description="Status da exclusão")
    message: str = Field(..., description="Mensagem descritiva")
