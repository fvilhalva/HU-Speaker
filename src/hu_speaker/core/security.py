"""Segurança da API."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header, HTTPException, status  # type: ignore[import]
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


def require_service_jwt(authorization: str | None = Header(default=None, alias="Authorization")) -> AuthContext:
    """Valida o JWT assinado do sistema chamador."""
    settings = get_settings()

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
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