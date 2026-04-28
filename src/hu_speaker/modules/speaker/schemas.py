"""Schemas (DTOs) para o módulo de Speaker."""

from pydantic import BaseModel, Field


class SynthesisRequest(BaseModel):
    """Requisição para síntese de voz."""

    text: str = Field(..., min_length=1, max_length=1000, description="Texto a ser sintetizado")
    language: str = Field(default="pt_BR", description="Idioma para síntese")


class SynthesisResponse(BaseModel):
    """Resposta da síntese de voz."""

    id: str = Field(..., description="ID único da requisição")
    text: str = Field(..., description="Texto sintetizado")
    language: str = Field(..., description="Idioma utilizado")
    status: str = Field(..., description="Status da síntese")
