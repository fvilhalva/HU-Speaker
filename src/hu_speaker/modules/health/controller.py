"""Controller de Health Check."""

from hu_speaker.modules.health.service import HealthService


class HealthController:
    """Controller para endpoints de Health Check."""

    def __init__(self, service: HealthService | None = None) -> None:
        """Inicializa o controller com o serviço de health."""
        self.service = service or HealthService()

    def get_health(self) -> dict[str, str]:
        """Retorna o status de saúde da aplicação."""
        return self.service.check_status()

    def get_readiness(self) -> dict[str, str]:
        """Retorna o status de prontidão da aplicação."""
        return self.service.check_readiness()
