"""Factory de criação da aplicação FastAPI."""

import time
from threading import Thread

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hu_speaker.core.config import Settings, get_settings
from hu_speaker.modules.common.router import router as common_router
from hu_speaker.modules.health.router import router as health_router
from hu_speaker.modules.speaker.router import router as speaker_router


def start_cleanup_task(settings: Settings) -> Thread | None:
    """Inicia thread de limpeza de arquivos antigos.

    Args:
        settings: Objeto de configurações

    Returns:
        Thread daemon iniciada, ou None se a limpeza estiver desabilitada
    """
    if not settings.ENABLE_CLEANUP:
        return None

    def cleanup_loop() -> None:
        from hu_speaker.modules.speaker.cleanup_task import (
            cleanup_old_audio_files,
            get_audio_dir_stats,
        )
        
        while True:
            try:
                deleted = cleanup_old_audio_files(
                    settings.AUDIO_OUTPUT_DIR,
                    ttl_minutes=settings.CLEANUP_TTL_MINUTES,
                )
                
                if deleted > 0:
                    stats = get_audio_dir_stats(settings.AUDIO_OUTPUT_DIR)
                    if stats is not None:
                        print(
                            f"✅ Cleanup completed: {deleted} files removed | "
                            f"Stats: {stats['file_count']} files, "
                            f"{stats['total_size_mb']:.1f}MB total"
                        )
                
            except Exception as e:
                print(f"⚠️  Cleanup task error: {e}")
            
            time.sleep(settings.CLEANUP_INTERVAL_SECONDS)
    
    thread = Thread(target=cleanup_loop, daemon=True)
    thread.start()
    return thread


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API de síntese de voz para o Hospital Universitário da UFGD",
        debug=settings.DEBUG,
    )

    # CORS: permite que o painel (outra origem, ex.: http://localhost:9000)
    # chame a API pelo navegador. As origens vêm de settings.CORS_ORIGINS
    # (lista separada por vírgula).
    cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registrar routers dos módulos
    app.include_router(common_router)
    app.include_router(health_router)
    app.include_router(speaker_router)

    # Iniciar task de limpeza de arquivos antigos
    if settings.ENABLE_CLEANUP:
        @app.on_event("startup")
        def startup_cleanup() -> None:
            cleanup_thread = start_cleanup_task(settings)
            if cleanup_thread:
                print(f"🗑️  Audio cleanup task started (TTL: {settings.CLEANUP_TTL_MINUTES}min)")

    return app
