"""Factory de criação da aplicação FastAPI."""

from fastapi import FastAPI  # type: ignore[import]

from hu_speaker.core.config import get_settings
from hu_speaker.modules.common.router import router as common_router
from hu_speaker.modules.health.router import router as health_router
from hu_speaker.modules.speaker.router import router as speaker_router


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API de síntese de voz para o Hospital Universitário da UFGD",
        debug=settings.DEBUG,
    )

    # Registrar routers dos módulos
    app.include_router(common_router)
    app.include_router(health_router)
    app.include_router(speaker_router)

    return app
