# HU-Speaker

HU-Speaker e uma API de sintese de voz (TTS) desenvolvida para o Hospital Universitario da UFGD (Rede Ebserh/MS). Ela utiliza o Piper TTS para receber requisicoes do sistema de gestao hospitalar e gerar, em tempo real, audios para nomes, senhas e tokens, apoiando a convocacao audivel de pacientes nas areas de triagem e consultorios.

## Estrutura

```text
.
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements-dev.txt
├── src/
│   └── hu_speaker/
│       ├── __init__.py
│       ├── main.py (entry point)
│       ├── app.py (factory da aplicação)
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py (configurações)
│       │   └── exceptions.py (exceções customizadas)
│       └── modules/
│           ├── common/
│           │   ├── __init__.py
│           │   └── router.py (rotas genéricas)
│           ├── health/
│           │   ├── __init__.py
│           │   ├── controller.py
│           │   ├── service.py
│           │   └── router.py
│           └── speaker/
│               ├── __init__.py
│               ├── controller.py
│               ├── service.py
│               ├── schemas.py (DTOs)
│               └── router.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── integration/
    │   ├── __init__.py
    │   └── test_api.py
    └── unit/
        ├── __init__.py
        ├── test_health_service.py
        └── test_speaker_service.py
```

## Requisitos

- Python 3.11+

## Arquitetura

O projeto segue um padrão modular inspirado em NestJS:

- **Core**: Configurações centrais, exceções e utilitários globais.
- **Modules**: Funcionalidades organizadas em módulos independentes com:
  - `controller.py`: Lógica de orquestração e manipulação de requisições.
  - `service.py`: Lógica de negócio.
  - `router.py`: Registro das rotas FastAPI.
  - `schemas.py`: Validação de dados (DTOs) com Pydantic.

### Variáveis de Ambiente

A aplicação carrega configurações do arquivo `.env` usando `pydantic-settings`. Variáveis importantes:

- **ENVIRONMENT**: `development`, `staging` ou `production`
- **DEBUG**: Ativa modo de debug (recarregamento automático)
- **JWT_SECRET_KEY**: Chave secreta para tokens JWT (mude em produção)
- **DATABASE_URL**: URL de conexão PostgreSQL (se usar banco de dados)
- **HIS_API_URL/HIS_API_KEY**: Integração com Sistema de Informação Hospitalar
- **SMTP_*** : Configurações para envio de emails (notificações)

Ver `.env.example` para a lista completa de variáveis.

## Setup rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Configuração de Ambiente

1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. Preencha o `.env` com suas configurações:
```
DEBUG=true
PORT=8082
DATABASE_URL=postgresql://user:password@localhost:5432/db
JWT_SECRET_KEY=sua-chave-secreta-aqui
HIS_API_URL=http://seu-his.hospital.local:8080/api
HIS_API_KEY=sua-api-key-aqui
```

**Importante**: Nunca commite o arquivo `.env`. Ele contém dados sigilosos e é ignorado pelo Git.

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

Depois, acesse a API em `http://localhost:8082`.

## Proximos passos sugeridos

1. Ajustar metadados em `pyproject.toml` (nome, autor, descricao).
2. Adicionar dependencias em `[project.dependencies]`.
3. Expandir o pacote em `src/hu_speaker` com os modulos da aplicacao.