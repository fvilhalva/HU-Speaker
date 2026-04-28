# HU-Speaker

HU-Speaker (Motor de Chamada de Pacientes) e uma API de sintese de voz (TTS) desenvolvida para o Hospital Universitario da UFGD (Rede Ebserh/MS) com o objetivo de otimizar o fluxo de atendimento. O servico utiliza o Piper TTS para receber requisicoes do sistema de gestao hospitalar e gerar, em tempo real, os audios correspondentes a nomes, senhas e tokens. A aplicacao atua como o motor central responsavel pela convocacao audivel dos pacientes nas areas de triagem e consultorios.

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
docker run --rm -p 8082:8082 hu-speaker
```

### Subir com Docker Compose

```bash
docker compose up
docker compose up --build
```

## Proximos passos sugeridos

1. Ajustar metadados em `pyproject.toml` (nome, autor, descricao).
2. Adicionar dependencias em `[project.dependencies]`.
3. Expandir o pacote em `src/hu_speaker` com os modulos da aplicacao.