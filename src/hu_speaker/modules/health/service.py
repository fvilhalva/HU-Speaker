"""Service de Health Check."""


class HealthService:
    """Serviço de verificação de saúde da aplicação."""

    def check_status(self) -> dict[str, str]:
        """Verifica o status geral da aplicação."""
        return {"status": "ok"}

    def check_readiness(self) -> dict[str, str]:
        """Verifica se a aplicação está pronta para receber requisições."""
        return {"ready": True}
