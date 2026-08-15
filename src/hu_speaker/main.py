"""Ponto de entrada da aplicação."""

import uvicorn

from hu_speaker.app import create_app
from hu_speaker.core.config import get_settings

app = create_app()


def run() -> None:
    """Executa a API localmente."""
    settings = get_settings()

    uvicorn.run(
        "hu_speaker.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    run()
