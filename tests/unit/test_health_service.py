"""Testes unitários do módulo de Health."""

from hu_speaker.modules.health.service import HealthService


def test_health_service_check_status() -> None:
    """Testa o status de saúde."""
    service = HealthService()
    result = service.check_status()

    assert result["status"] == "ok"


def test_health_service_check_readiness() -> None:
    """Testa o status de prontidão."""
    service = HealthService()
    result = service.check_readiness()

    assert result["ready"] is True
