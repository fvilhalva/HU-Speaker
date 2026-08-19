FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# espeak-ng: back-end de fonemização usado pelo Kokoro para pt-BR.
RUN apt-get update \
    && apt-get install -y --no-install-recommends espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Copy only pyproject.toml first (changes less frequently)
COPY pyproject.toml README.md /app/

# torch em modo CPU (o índice cpu evita baixar o build CUDA, que é enorme).
# Instalado ANTES de `pip install .` para que o kokoro encontre torch pronto.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install dependencies (will be cached if pyproject.toml doesn't change)
RUN pip install --no-cache-dir .

# Workaround: o misaki (fonemizador do Kokoro) procura os dados do espeak-ng
# na RAIZ do pacote espeakng_loader, mas eles ficam no subdiretório
# espeak-ng-data/. Sem isso, a síntese Kokoro falha com "phontab: No such
# file or directory". Aqui criamos symlinks dos dados para a raiz do pacote.
RUN python - <<'PY'
import os, glob, espeakng_loader
pkg = os.path.dirname(espeakng_loader.__file__)
data = espeakng_loader.get_data_path()
linked = 0
for src in glob.glob(os.path.join(data, "*")):
    dst = os.path.join(pkg, os.path.basename(src))
    if not os.path.exists(dst):
        try:
            os.symlink(src, dst)
            linked += 1
        except OSError:
            pass
print(f"espeak-ng data linkado para {pkg} ({linked} itens)")
PY

# Copy source code (changes more frequently)
COPY src /app/src

# Pré-carrega o modelo Kokoro (pesos + voz pt-BR) no build, para não haver
# download na primeira chamada em produção. Não falha o build se não houver
# rede — nesse caso o download acontece no primeiro uso.
RUN python -c "import warnings; warnings.filterwarnings('ignore'); \
from kokoro import KPipeline; p = KPipeline(lang_code='p'); \
list(p('aquecimento', voice='pf_dora'))" || \
    echo "aviso: pré-carga do Kokoro pulada (sem rede no build)"

# Create appuser
RUN useradd -m appuser && chown -R appuser:appuser /app

USER appuser

EXPOSE 8082

CMD ["uvicorn", "hu_speaker.main:app", "--host", "0.0.0.0", "--port", "8082"]
