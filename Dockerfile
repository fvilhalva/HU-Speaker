FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Copy only pyproject.toml first (changes less frequently)
COPY pyproject.toml README.md /app/

# Install dependencies (will be cached if pyproject.toml doesn't change)
RUN pip install --no-cache-dir .

# Copy source code (changes more frequently)
COPY src /app/src

# Create appuser
RUN useradd -m appuser && chown -R appuser:appuser /app

USER appuser

EXPOSE 8082

CMD ["uvicorn", "hu_speaker.main:app", "--host", "0.0.0.0", "--port", "8082"]