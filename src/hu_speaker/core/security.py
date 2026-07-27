"""Segurança da API."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header, HTTPException, Query, status  # type: ignore[import]
import jwt
from jwt import InvalidTokenError

from hu_speaker.core.config import get_settings


@dataclass(frozen=True)
class AuthContext:
    """Contexto autenticado derivado do JWT do sistema chamador."""

    subject: str
    source_system: str | None = None
    actor_id: str | None = None
    actor_name: str | None = None
    actor_role: str | None = None
    request_id: str | None = None


def require_service_jwt(
    authorization: str | None = Header(default=None, alias="Authorization"),
    token_qs: str | None = Query(default=None, alias="token"),
) -> AuthContext:
    """Valida o JWT assinado do sistema chamador.

    O token pode vir no header ``Authorization: Bearer <jwt>`` (uso normal via
    API) ou, como alternativa, na query string ``?token=<jwt>``. O fallback por
    query string existe porque o navegador nao envia cabecalhos ao reproduzir
    audio diretamente (elemento <audio>), o que e necessario para o painel tocar
    o nome do paciente a partir do endpoint de download.
    """
    settings = get_settings()

    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
    elif token_qs:
        token = token_qs.strip()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    return AuthContext(
        subject=str(payload["sub"]),
        source_system=payload.get("source_system"),
        actor_id=payload.get("actor_id"),
        actor_name=payload.get("actor_name"),
        actor_role=payload.get("actor_role"),
        request_id=payload.get("request_id"),
    )


def get_audit_context_from_claims(auth: AuthContext) -> AuthContext:
    """Reaproveita os próprios claims como contexto de auditoria."""
    return auth