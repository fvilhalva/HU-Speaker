FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias primeiro para aproveitar melhor o cache de camadas
COPY pyproject.toml README.md /app/
RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.30.0" \
    "httpx>=0.27.0" \
    "piper-tts"

# Copia o codigo e instala apenas o pacote local
COPY src /app/src
RUN pip install --no-cache-dir --no-deps .

# Executa sem privilegios de root
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "hu_speaker.main:app", "--host", "0.0.0.0", "--port", "8000"]
