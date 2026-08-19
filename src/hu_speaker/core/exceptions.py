"""Exceções customizadas da aplicação."""

from fastapi import HTTPException, status


class APIException(HTTPException):
    """Exceção base para erros da API."""

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Inicializa a exceção."""
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ServiceUnavailable(APIException):
    """Serviço indisponível."""

    def __init__(self, detail: str = "Serviço indisponível") -> None:
        """Inicializa a exceção."""
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class UnknownModelError(APIException):
    """Modelo de voz solicitado não existe."""

    def __init__(self, model: str, available: tuple[str, ...] | list[str]) -> None:
        """Inicializa a exceção com a lista de modelos disponíveis."""
        super().__init__(
            detail=f"Unknown TTS model '{model}'. Available: {', '.join(available)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
