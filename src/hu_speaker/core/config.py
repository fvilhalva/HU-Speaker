"""Configurações da aplicação."""

from functools import lru_cache

from pydantic_settings import BaseSettings # type: ignore[import]


class Settings(BaseSettings):
    """Configurações globais da aplicação."""

    # Aplicação
    APP_NAME: str = "HU-Speaker API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False

    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8082

    # Banco de dados
    DATABASE_URL: str = ""  # postgresql://user:password@host:5432/db

    # Autenticação
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SERVICE_API_KEY: str = ""

    # Integrações
    HIS_API_URL: str = ""  # URL do Sistema de Informação Hospitalar
    HIS_API_KEY: str = ""  # API key para integração com HIS
    HIS_API_TIMEOUT: int = 30

    # Piper TTS
    PIPER_MODEL: str = "pt_BR-faber-medium.onnx"
    PIPER_SPEAKERS: str = "0"  # Índice do speaker
    AUDIO_OUTPUT_DIR: str = "/tmp/hu-speaker-audio"
    MAX_TEXT_LENGTH: int = 1000

    # Audio Cleanup (limpeza de arquivos antigos)
    CLEANUP_TTL_MINUTES: int = 10  # Tempo em minutos para manter arquivos WAV
    CLEANUP_INTERVAL_SECONDS: int = 60  # Verificar limpeza a cada minuto
    ENABLE_CLEANUP: bool = True  # Habilitar task de limpeza automática

    # Email (notificações)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "hu-speaker@hospital.local"
    SMTP_TLS: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:9000,http://127.0.0.1:9000"  # Separado por vírgula

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/var/log/hu-speaker/app.log"

    class Config:
        """Configuração do Pydantic."""

        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Retorna as configurações da aplicação (cached)."""
    return Settings()


settings = get_settings()
