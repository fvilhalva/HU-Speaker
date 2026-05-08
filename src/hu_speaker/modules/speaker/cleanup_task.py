"""Background task para limpeza de arquivos WAV antigos."""

import time
from pathlib import Path
from typing import Optional


def cleanup_old_audio_files(audio_dir: str, ttl_minutes: int = 5) -> int:
    """Remove WAV files older than TTL.
    
    Args:
        audio_dir: Diretório com arquivos de áudio
        ttl_minutes: Tempo em minutos para manter arquivos (padrão: 5)
    
    Returns:
        Número de arquivos deletados
    """
    audio_path = Path(audio_dir)
    if not audio_path.exists():
        return 0
    
    deleted_count = 0
    now = time.time()
    ttl_seconds = ttl_minutes * 60
    
    for wav_file in audio_path.glob("*.wav"):
        try:
            file_age = now - wav_file.stat().st_mtime
            if file_age > ttl_seconds:
                wav_file.unlink()
                deleted_count += 1
                age_minutes = file_age / 60
                print(f"🗑️  Deleted: {wav_file.name} ({age_minutes:.0f}min old)")
        except OSError as e:
            print(f"⚠️  Error deleting {wav_file.name}: {e}")
    
    return deleted_count


def get_audio_dir_stats(audio_dir: str) -> Optional[dict]:
    """Retorna estatísticas do diretório de áudio.
    
    Args:
        audio_dir: Diretório com arquivos de áudio
    
    Returns:
        Dict com file_count, total_size_mb, oldest_file_age_min
    """
    audio_path = Path(audio_dir)
    if not audio_path.exists():
        return None
    
    wav_files = list(audio_path.glob("*.wav"))
    if not wav_files:
        return {"file_count": 0, "total_size_mb": 0.0, "oldest_file_age_min": 0}
    
    now = time.time()
    total_size = sum(f.stat().st_size for f in wav_files)
    oldest_age = max(now - f.stat().st_mtime for f in wav_files)
    
    return {
        "file_count": len(wav_files),
        "total_size_mb": total_size / (1024 * 1024),
        "oldest_file_age_min": oldest_age / 60,
    }
