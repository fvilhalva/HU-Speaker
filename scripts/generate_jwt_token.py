#!/usr/bin/env python3
"""Script para gerar tokens JWT para testes locais."""

import os
import sys
from datetime import UTC, datetime, timedelta

import jwt

# Importar config do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.hu_speaker.core.config import get_settings  # noqa: E402


def generate_token(
    subject: str = "novosga-service",
    source_system: str = "novosga",
    actor_id: str = "123",
    actor_name: str = "Maria Silva",
    actor_role: str = "attendant",
    request_id: str = "req-001",
    expires_in_minutes: int = 720,
) -> str:
    """Gera um JWT válido para testes."""
    settings = get_settings()
    
    payload = {
        "sub": subject,
        "source_system": source_system,
        "actor_id": actor_id,
        "actor_name": actor_name,
        "actor_role": actor_role,
        "request_id": request_id,
        "exp": datetime.now(UTC) + timedelta(minutes=expires_in_minutes),
        "iat": datetime.now(UTC),
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def main():
    """Gera token e exibe instruções."""
    token = generate_token()
    
    print("=" * 80)
    print("✓ Token JWT gerado com sucesso!")
    print("=" * 80)
    print()
    print("Token (válido por 12 horas):")
    print(token)
    print()
    print("INSTRUÇÕES POSTMAN:")
    print("1. Abra Postman")
    print("2. Vá para Variables (lado direito)")
    print("3. Defina jwt_token com o valor acima")
    print("4. Faça qualquer requisição - o header Authorization será enviado automaticamente")
    print()
    print("TESTE RÁPIDO:")
    print("  curl -X POST http://localhost:8082/speak/synthesize \\")
    print("    -H 'Authorization: Bearer " + token + "' \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"text\": \"Olá\", \"language\": \"pt_BR\"}'")
    print()


if __name__ == "__main__":
    main()
