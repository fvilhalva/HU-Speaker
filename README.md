# HU-Speaker

Template base para projeto Python com FastAPI, testes e ferramentas de qualidade.

## Estrutura

```text
.
├── pyproject.toml
├── requirements-dev.txt
├── src/
│   └── hu_speaker/
│       ├── __init__.py
│       └── main.py
└── tests/
	└── test_main.py
```

## Requisitos

- Python 3.11+

## Setup rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Como executar (API)

```bash
uvicorn hu_speaker.main:app --reload
```

ou via script do projeto:

```bash
hu-speaker
```

### Endpoints iniciais

- `GET /health` retorna status de disponibilidade da API.

### Documentacao automatica

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testes

```bash
pytest
```

## Qualidade de codigo

```bash
ruff check .
mypy src
```

## Docker

```bash
docker build -t hu-speaker .
docker run --rm -p 8000:8000 hu-speaker
```

## Proximos passos sugeridos

1. Ajustar metadados em `pyproject.toml` (nome, autor, descricao).
2. Adicionar dependencias em `[project.dependencies]`.
3. Expandir o pacote em `src/hu_speaker` com os modulos da aplicacao.