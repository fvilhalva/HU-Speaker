"""Router de rotas comuns."""

from fastapi import APIRouter, Response

router = APIRouter(tags=["common"])


@router.get("/", response_model=dict[str, str])
def root() -> dict[str, str]:
    """Rota inicial da API."""
    return {"message": "HU-Speaker API online"}


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Retorna vazio para evitar 404 do navegador ao pedir favicon."""
    return Response(status_code=204)
