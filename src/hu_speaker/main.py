"""Aplicacao FastAPI e ponto de entrada local."""

from fastapi import FastAPI
from fastapi import Response
import uvicorn

app = FastAPI(title="HU-Speaker API", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    """Rota inicial para evitar 404 ao abrir no navegador."""
    return {"message": "HU-Speaker API online"}


@app.get("/health")
def health() -> dict[str, str]:
    """Endpoint simples para verificacao de disponibilidade."""
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Retorna vazio para evitar 404 do navegador ao pedir favicon."""
    return Response(status_code=204)


def run() -> None:
    """Executa a API localmente sem reload."""
    uvicorn.run("hu_speaker.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
