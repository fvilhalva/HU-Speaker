"""Router de Health Check."""

from fastapi import APIRouter

from hu_speaker.modules.health.controller import HealthController

router = APIRouter(prefix="/health", tags=["health"])
health_controller = HealthController()


@router.get("", response_model=dict[str, str])
def get_health() -> dict[str, str]:
    """Retorna o status de saúde da aplicação."""
    return health_controller.get_health()


@router.get("/ready", response_model=dict[str, bool])
def get_readiness() -> dict[str, bool]:
    """Verifica se a aplicação está pronta."""
    return health_controller.get_readiness()
