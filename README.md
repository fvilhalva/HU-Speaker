# HU-Speaker

HU-Speaker é uma API de síntese de voz (TTS) desenvolvida para o Hospital Universitário da UFGD (Rede Ebserh/MS). Ela utiliza o Piper TTS para receber requisições do sistema de gestão hospitalar e gerar, em tempo real, áudios para nomes, senhas e tokens, apoiando a convocação audível de pacientes nas áreas de triagem e consultórios.

## 🚀 Status

✅ **Funcional e pronto para uso**
- Síntese de voz com Piper TTS real (português brasileiro)
- Download de áudio em WAV (16-bit PCM mono 22050 Hz)
- Controle de velocidade (acessibilidade para idosos - até 75% mais devagar)
- API REST moderna com FastAPI
- Containerizado com Docker Compose

---

## 📋 Índice Rápido

### Usuário Final
1. [Setup Rápido](#-setup-rápido)
2. [Como Usar](#-como-usar)
3. [Velocidade de Áudio](#-velocidade-de-áudio)
4. [Endpoints](#-endpoints)

### Desenvolvedor
5. [Estrutura do Projeto](#-estrutura-do-projeto)
6. [Desenvolvimento](#-desenvolvimento)
7. [Variáveis de Ambiente](#-variáveis-de-ambiente)
8. [Testes](#-testes)
9. [Docker](#-docker)
10. [Troubleshooting](#-troubleshooting)

### Arquitetura & Roadmap
11. [Arquitetura](#-arquitetura)
12. [Roadmap](#-roadmap)
13. [Próximos Passos](#-próximos-passos)
14. [Acessibilidade](#-acessibilidade)

---

## Setup Rápido

### 1. Com Docker (Recomendado)

```bash
docker compose up
```

A API estará em `http://localhost:8082`

### 2. Local (Python 3.11+)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Copiar variáveis de ambiente
cp .env.example .env

# Rodar
uvicorn hu_speaker.main:app --reload
```

---

## Como Usar

### cURL

#### 1. Sintetizar Áudio

```bash
curl -X POST http://localhost:8082/speak/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bem-vindo ao HU-Speaker",
    "language": "pt_BR",
    "length_scale": 1.0
  }'
```

**Resposta:**
```json
{
  "id": "798d5acd-bb00-46de-b6b1-6a8d139d7a0f",
  "text": "Bem-vindo ao HU-Speaker",
  "language": "pt_BR",
  "status": "completed"
}
```

#### 2. Baixar Áudio

```bash
curl -o audio.wav http://localhost:8082/speak/download/798d5acd-bb00-46de-b6b1-6a8d139d7a0f
```

#### 3. Verificar Status

```bash
curl http://localhost:8082/speak/status/798d5acd-bb00-46de-b6b1-6a8d139d7a0f
```

### Postman

1. **Importar a collection**:
   - Abra Postman → **File > Import**
   - Selecione `postman_collection.json`

2. **Usar as requisições prontas**:
   - "Synthesize - Curto" (velocidade normal)
   - "Synthesize - Para Idosos" (40% mais devagar)
   - "Download Audio" (baixar WAV)

Veja [Configurar Variáveis](#variáveis-no-postman) para automatizar o fluxo.

#### Variáveis no Postman

1. Clique em **Environments** (canto inferior esquerdo)
2. Crie um novo environment com:
   ```
   base_url: http://localhost:8082
   synthesis_id: (será preenchido automaticamente)
   ```

3. Nas URLs, use: `{{base_url}}/speak/synthesize`

---

## Velocidade de Áudio

Use o parâmetro `length_scale` para adaptar a velocidade:

| Valor | Velocidade | Caso de Uso |
|-------|-----------|-----------|
| **0.5** | 50% rápido | Áudio acelerado |
| **0.8** | 20% rápido | Um pouco mais rápido |
| **1.0** | Normal | ✅ Padrão (natural) |
| **1.3** | 30% devagar | Compreensão melhorada |
| **1.4** | 40% devagar | ✅ **Ideal para idosos** |
| **1.5-2.0** | Muito devagar | Deficiência auditiva severa |

### Exemplos

**Pra idosos:**
```bash
curl -X POST http://localhost:8082/speak/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Paciente número 45",
    "language": "pt_BR",
    "length_scale": 1.4
  }'
```

**Aprendizado de língua:**
```bash
curl -X POST http://localhost:8082/speak/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Isso é uma frase em português",
    "language": "pt_BR",
    "length_scale": 1.5
  }'
```

---

## Endpoints

### `POST /speak/synthesize`

Sintetiza um texto em áudio.

**Body (JSON):**
```json
{
  "text": "Seu texto aqui",
  "language": "pt_BR",
  "length_scale": 1.0
}
```

**Parâmetros:**
- `text` (obrigatório): 1-1000 caracteres
- `language` (opcional): Idioma. Padrão: `"pt_BR"`
- `length_scale` (opcional): Velocidade (0.5-2.0). Padrão: `1.0`

**Resposta:**
```json
{
  "id": "uuid",
  "text": "Seu texto aqui",
  "language": "pt_BR",
  "status": "completed"
}
```

---

### `GET /speak/download/{id}`

Baixa o arquivo WAV sintetizado.

**Exemplo:**
```bash
curl -o audio.wav http://localhost:8082/speak/download/798d5acd-bb00-46de-b6b1-6a8d139d7a0f
```

**Formato:** WAVE PCM 16-bit mono 22050 Hz

### `DELETE /speak/{id}`

Exclui imediatamente o arquivo WAV sintetizado e remove os metadados em memória.

**Resposta:**
```json
{
  "id": "798d5acd-bb00-46de-b6b1-6a8d139d7a0f",
  "status": "deleted",
  "message": "Audio deleted successfully"
}
```

---

### `GET /speak/status/{id}`

Retorna o status de uma síntese.

**Resposta:**
```json
{
  "id": "798d5acd-bb00-46de-b6b1-6a8d139d7a0f",
  "status": "completed"
}
```

---

## Variáveis de Ambiente

As principais variáveis do fluxo de áudio são:

- `AUDIO_OUTPUT_DIR=/tmp/hu-speaker-audio`
- `ENABLE_CLEANUP=true`
- `CLEANUP_TTL_MINUTES=10`
- `CLEANUP_INTERVAL_SECONDS=60`

Com isso, os arquivos WAV ficam em um diretório temporário e a limpeza roda com retenção máxima aproximada de 10 a 11 minutos, dependendo do intervalo de execução.

---

### `GET /health`

Health check da API.

**Resposta:**
```json
{
  "status": "ok"
}
```

---

### `GET /health/ready`

Readiness check (verifica se a API está pronta).

---

## Estrutura

```
.
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── postman_collection.json    # 👈 Importar no Postman
├── scripts/
│   └── integration_test.py     # Teste end-to-end
├── src/
│   └── hu_speaker/
│       ├── __init__.py
│       ├── main.py             # Entry point
│       ├── app.py              # Factory da aplicação
│       ├── core/
│       │   ├── config.py        # Configurações (Pydantic)
│       │   └── exceptions.py    # Exceções customizadas
│       └── modules/
│           ├── common/          # Rotas genéricas
│           ├── health/          # Health checks
│           └── speaker/         # TTS (síntese)
│               ├── controller.py
│               ├── service.py
│               ├── schemas.py   # DTOs
│               └── router.py
└── tests/
    ├── integration/
    └── unit/
```

### Arquitetura

O projeto segue um padrão **modular inspirado em NestJS**:

- **Core**: Configurações centrais, exceções
- **Modules**: Funcionalidades independentes com:
  - `controller.py` - Orquestração de requisições
  - `service.py` - Lógica de negócio
  - `router.py` - Rotas FastAPI
  - `schemas.py` - Validação (Pydantic DTOs)

---

## 👨‍💻 Desenvolvimento

### Variáveis de Ambiente

**Setup inicial:**
```bash
cp .env.example .env
```

**Arquivo `.env` (NUNCA comitar):**
- Contém dados sensíveis
- Está no `.gitignore`
- Use valores reais em desenvolvimento/produção

**Arquivo `.env.example` (SEMPRE comitar):**
- Template com valores de exemplo
- Seguro compartilhar
- Referência para novos desenvolvedores

### Principais Variáveis

| Variável | Exemplo | Descrição |
|----------|---------|-----------|
| `DEBUG` | `true` | Reload automático em dev |
| `ENVIRONMENT` | `development` | `development`, `staging`, `production` |
| `PORT` | `8082` | Porta da API |
| `PIPER_MODEL` | `pt_BR-faber-medium.onnx` | Modelo TTS |
| `AUDIO_OUTPUT_DIR` | `/tmp/hu-speaker-audio` | Onde salvar WAVs |
| `JWT_SECRET_KEY` | (gerar nova) | Chave secreta JWT |
| `HIS_API_URL` | (seu HIS) | URL do Sistema de Informação Hospitalar |
| `HIS_API_KEY` | (seu token) | Token de autenticação HIS |
| `SMTP_HOST`, `SMTP_PORT` | (seu SMTP) | Para enviar emails |
| `DATABASE_URL` | (PostgreSQL) | Para quando implementar BD |

### Gerar JWT_SECRET_KEY (Produção)

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🧪 Testes

**Integration test (recomendado):**
```bash
python3 scripts/integration_test.py
```

Valida:
- ✅ POST /speak/synthesize
- ✅ GET /speak/download/{id} retorna WAV válido
- ✅ Arquivo contém áudio real
- ✅ GET /speak/status/{id}

**Unit tests:**
```bash
pytest tests/unit/
```

**Qualidade de código:**
```bash
ruff check .      # Linting
mypy src          # Type checking
```

---

## Docker

### Build

```bash
docker build -t hu-speaker .
```

### Run

```bash
docker run --rm -p 8082:8082 hu-speaker
```

### Compose

```bash
# Iniciar
docker compose up

# Rebuild
docker compose up --build

# Parar
docker compose down

# Logs
docker compose logs -f hu-speaker
```

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| `Connection refused` | Certifique `docker compose up -d` está rodando |
| `400 Bad Request` | Verifique JSON válido no Body |
| `404 Not Found` | ID expirou, resintetize |
| `empty WAV file` | ❌ BUG FIXO - usamos `synthesize_wav()` agora |

---

## 📚 Documentação Adicional

- **[ENVIRONMENT.md](ENVIRONMENT.md)** - Todas as variáveis de ambiente
- **[ROADMAP.md](ROADMAP.md)** - Plano de desenvolvimento (7 fases)
- **[NEXT_STEPS.md](NEXT_STEPS.md)** - Próximas ações recomendadas

---

## 📚 Documentação

Esta API foi desenvolvida com foco em **inclusão social**:

✅ **Controle de velocidade**: Idosos e deficientes auditivos (até 75% mais devagar)  
✅ **Áudio claro**: 16-bit PCM 22050 Hz (qualidade de voz natural)  
✅ **Integração fácil**: JSON simples, sem complexidade  
✅ **Download de áudio**: Compatível com qualquer player  

### Casos de Uso

| Grupo | length_scale | Razão |
|-------|-------------|-------|
| Pessoa com audição normal | 1.0 | Velocidade natural |
| Idoso | 1.4 | Compreensão facilitada |
| Deficiência auditiva | 1.5-2.0 | Velocidade muito reduzida |
| Estudando português | 1.3-1.5 | Melhor absorção de pronúncia |

---

## 🛣️ Roadmap

### ✅ Fase 1: Core (CONCLUÍDO)

- [x] Piper TTS real funcional
- [x] Download de áudio WAV
- [x] Controle de velocidade (acessibilidade)
- [x] Docker + Docker Compose
- [x] Testes de integração

### 🔄 Fase 2: Segurança & Dados (Próximas 2-4 semanas)

- [ ] Autenticação JWT
- [ ] Banco de dados PostgreSQL
- [ ] Logging e auditoria (LGPD/HIPAA)
- [ ] Rate limiting (proteção contra abuso)

### 📅 Fase 3: Integração Hospitalar (4-8 semanas)

- [ ] Integração com HIS (Sistema de Informação Hospitalar)
- [ ] Sincronização de pacientes
- [ ] Webhooks para notificações

### 🚀 Fase 4: Performance (8-12 semanas)

- [ ] Fila de processamento (Celery + Redis)
- [ ] Cache de sínteses
- [ ] Processamento paralelo

### 📊 Fase 5: Observabilidade (12-16 semanas)

- [ ] Prometheus (métricas)
- [ ] Grafana (dashboards)
- [ ] ELK Stack (logs centralizados)
- [ ] Sentry (error tracking)

### 🐳 Fase 6: Infraestrutura (16-20 semanas)

- [ ] Kubernetes manifests
- [ ] Helm charts
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Staging + Production

### 📚 Fase 7: Documentação (20+ semanas)

- [ ] API docs completa
- [ ] Developer guide
- [ ] Deployment runbook
- [ ] Disaster recovery plan

---

## 📝 Próximos Passos (Sprint 1)

### IMEDIATO (próximas 2 semanas)

#### Prioridade 1: Autenticação JWT
```bash
# Criar módulo auth/
src/hu_speaker/modules/auth/
├── controller.py
├── service.py
├── schemas.py
└── router.py
```

- [ ] `POST /auth/login` - Login com email/senha
- [ ] `POST /auth/refresh` - Renovar token
- [ ] Validar token em endpoints protegidos
- [ ] Hash de senhas com `passlib`

#### Prioridade 2: Banco de Dados
- [ ] Adicionar `sqlalchemy`, `psycopg2`, `alembic`
- [ ] Criar models: User, AudioLog, CallRecord
- [ ] PostgreSQL no Docker Compose
- [ ] Migrations automáticas

#### Prioridade 3: Testes Completos (80%+ coverage)
- [ ] Unit tests para todos os services
- [ ] Testes de integração (mocks de Piper)
- [ ] Testes de autenticação
- [ ] CI/CD básico (GitHub Actions)

### Checklist Sprint 1

```
Code Quality:
  [ ] 80%+ test coverage
  [ ] ruff/mypy sem erros
  [ ] bandit security scan passing

Documentation:
  [ ] ✅ README completo
  [ ] Swagger descriptions
  [ ] Developer guide

Security:
  [ ] JWT autenticação
  [ ] Senhas hashadas
  [ ] Input validation

Deployment:
  [ ] ✅ Docker funcional
  [ ] [ ] CI/CD pipeline basic
  [ ] [ ] Production checklist
```

### Como Começar

```bash
# 1. Clonar e setup
git clone <repo>
cd HU-Speaker
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# 2. Rodar em dev
docker compose up --build

# 3. Verificar status
curl http://localhost:8082/health

# 4. Começar implementação (ex: JWT)
git checkout -b feat/jwt-auth
# ... editar código ...
pytest tests/ -v
git commit -m "feat: add jwt authentication"
```

---

## 📐 Arquitetura

O projeto segue um padrão **modular inspirado em NestJS**:

```
Request HTTP
    ↓
Router (router.py)
    ↓
Controller (controller.py) ← Orquestração
    ↓
Service (service.py) ← Lógica de Negócio
    ↓
Piper TTS / Database / Externos
```

**Benefícios:**
- ✅ Fácil de testar (mock de service)
- ✅ Separação de responsabilidades
- ✅ Reutilizável em diferentes contextos
- ✅ Escalável

---

## 🔐 Segurança em Produção

### Checklist de Deploy

- [ ] Gerar novo `JWT_SECRET_KEY`
- [ ] `DEBUG=false`
- [ ] `ENVIRONMENT=production`
- [ ] Usar HTTPS/TLS (certificado SSL válido)
- [ ] Rate limiting habilitado
- [ ] Logs centralizados
- [ ] Backup do banco de dados
- [ ] Monitoramento ativo (Prometheus/Grafana)
- [ ] Auditoria de acesso (LGPD/HIPAA)
- [ ] Disaster recovery plan

### Variáveis de Produção

```bash
# Seguras vs Inseguras
ENVIRONMENT=production              # ✅ (não development)
DEBUG=false                         # ✅ (não true)
JWT_SECRET_KEY=<gerar_novo>         # ✅ (não default)
DATABASE_URL=postgresql://...       # ✅ (passworded)
ALLOWED_HOSTS=api.hospital.local    # ✅ (específico)
```

---

## 📞 Suporte

### Reportar Bugs

1. Descreva o problema com detalhe
2. Inclua versão da API: `curl http://localhost:8082/health`
3. Incluia logs: `docker compose logs hu-speaker`
4. Abra issue no GitHub

### Dúvidas?

- 📖 Leia [README.md](#) (você está aqui!)
- 🔧 Veja [Troubleshooting](#-troubleshooting)
- 💬 Abra uma issue no GitHub

---

## 📝 Licença

[Veja LICENSE](LICENSE)

---

## 👥 Autores

Desenvolvido para o **Hospital Universitário da UFGD** (Rede Ebserh/MS)

### Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feat/feature-name`)
3. Commit suas mudanças (`git commit -m "feat: descrição"`)
4. Push (`git push origin feat/feature-name`)
5. Abra Pull Request

---

**Última atualização:** 29 de Abril de 2026

✨ Built with ❤️ for Hospital Universitário UFGD