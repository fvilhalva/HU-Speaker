## 🚀 Próximos Passos - Quick Reference

### 📋 IMEDIATO (Sprint 1 - próximas 2 semanas)

```
PRIORIDADE 1: Implementar Piper TTS Real
├─ [ ] Refatorar SpeakerService para usar piper_tts de verdade
├─ [ ] Gerar arquivos WAV em AUDIO_OUTPUT_DIR
├─ [ ] Retornar URL/stream do áudio
├─ [ ] Suportar múltiplos idiomas
└─ [ ] Testes unitários para síntese

PRIORIDADE 2: Adicionar JWT + Autenticação
├─ [ ] Criar módulo auth/ (models, service, router)
├─ [ ] Endpoints: POST /auth/login, POST /auth/refresh
├─ [ ] Validar token em endpoints protegidos
├─ [ ] Hash de senhas com passlib
└─ [ ] Testes de autenticação

PRIORIDADE 3: Testes Completos (80%+ coverage)
├─ [ ] Testes unitários para services/controllers
├─ [ ] Testes de integração (E2E)
├─ [ ] Testes de autenticação
├─ [ ] Mock de Piper TTS e HIS
└─ [ ] CI/CD pipeline básico
```

---

### 📅 CURTO PRAZO (Sprint 2-3 - próximas 4 semanas)

```
TAREFA 1: Banco de Dados (PostgreSQL + SQLAlchemy)
├─ [ ] Adicionar dependências: sqlalchemy, psycopg2, alembic
├─ [ ] Configurar database connection
├─ [ ] Criar models: User, AudioLog, CallRecord
├─ [ ] Migrations com Alembic
└─ [ ] Docker Compose com PostgreSQL

TAREFA 2: Integração com HIS
├─ [ ] Criar módulo his/
├─ [ ] Endpoints: GET /his/patients, POST /his/call-patient
├─ [ ] Mock ou integração real com seu HIS
└─ [ ] Testes

TAREFA 3: Logging Estruturado + Auditoria
├─ [ ] Adicionar structlog ou python-json-logger
├─ [ ] Request ID tracing em middlewares
├─ [ ] Modelo AuditLog no BD
├─ [ ] Registrar acesso a dados de pacientes
└─ [ ] Teste de auditoria

TAREFA 4: CI/CD Pipeline
├─ [ ] GitHub Actions workflow
├─ [ ] Build Docker automático
├─ [ ] Executar testes em cada push
├─ [ ] Code quality checks (ruff, mypy)
└─ [ ] Deploy automático
```

---

### 💼 MÉDIO PRAZO (Sprint 4-5 - próximas 6 semanas)

```
TAREFA 1: Fila de Mensagens (Celery + Redis)
├─ [ ] Adicionar Redis ao Docker Compose
├─ [ ] Configurar Celery workers
├─ [ ] Task: generate_audio (background)
├─ [ ] Docker Compose com 3+ workers
└─ [ ] Testes de fila

TAREFA 2: Email + Notificações
├─ [ ] Criar módulo notifications/
├─ [ ] SMTP ou SendGrid integration
├─ [ ] Notificar admins de erros
├─ [ ] Notify users quando áudio pronto
└─ [ ] Testes

TAREFA 3: Rate Limiting + Proteção
├─ [ ] Adicionar slowapi
├─ [ ] Limitar por IP/usuário
├─ [ ] 100 req/min público, 1000/min autenticado
└─ [ ] Testes de rate limit

TAREFA 4: Documentação Completa
├─ [ ] Melhorar README com exemplos
├─ [ ] API docs (descrições detalhadas)
├─ [ ] Developer guide (como adicionar módulo)
├─ [ ] CONTRIBUTING.md
└─ [ ] Deployment guide
```

---

### 🏆 LONGO PRAZO (Sprint 6+)

```
[ ] Kubernetes manifests (Deployment, Service, Ingress)
[ ] Helm charts para fácil deploy
[ ] Prometheus + Grafana monitoring
[ ] ELK Stack ou Loki para logs centralizados
[ ] Performance tuning e load testing
[ ] Multi-tenancy (se necessário)
[ ] Disaster recovery plan
```

---

## 📊 Checklist por Tipo

### Code Quality
- [ ] 80%+ test coverage
- [ ] ruff/mypy passing
- [ ] bandit security scan passing
- [ ] pip-audit sem vulnerabilidades

### Documentation  
- [ ] ✅ README.md
- [ ] ✅ ENVIRONMENT.md
- [ ] ✅ ROADMAP.md
- [ ] [ ] API docs (Swagger descriptions)
- [ ] [ ] Developer guide
- [ ] [ ] Deployment runbook

### Security (LGPD/HIPAA)
- [ ] JWT autenticação
- [ ] Rate limiting
- [ ] Auditoria de acesso
- [ ] Criptografia de dados
- [ ] HTTPS/TLS
- [ ] Input validation

### Deployment
- [ ] ✅ Docker + Docker Compose
- [ ] [ ] CI/CD pipeline
- [ ] [ ] Kubernetes manifests
- [ ] [ ] Helm charts
- [ ] [ ] Monitoring (Prometheus)

---

## 📝 Exemplo: Como Começar Sprint 1

1. **Clonar/atualizar repo**
```bash
git clone <repo>
cd HU-Speaker
cp .env.example .env
```

2. **Instalar dependências**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

3. **Rodarcomo desenvolvimento**
```bash
docker compose up --build
# App rodando em http://localhost:8082
```

4. **Verificar atual status**
```bash
# Health check
curl http://localhost:8082/health

# Swagger docs
open http://localhost:8082/docs
```

5. **Começar implementação Piper TTS**
```bash
# Editar arquivo
vim src/hu_speaker/modules/speaker/service.py

# Rodar testes
pytest tests/ -v

# Commit
git commit -m "feat: implement real piper tts synthesis"
```

---

## 💡 Dicas

- ✅ Sempre escreva testes antes do código (TDD)
- ✅ Use feature branches (`git checkout -b feat/feature-name`)
- ✅ Pequenos commits (`git commit -m "feat: small change"`)
- ✅ Revise código antes de merge
- ✅ Documente decisões arquiteturais (ADRs)
- ✅ Considere LGPD/HIPAA desde o início

---

## 🎯 Resumo: Os 3 Passos Mais Importantes

### 1️⃣ Piper TTS Real (Core)
   *Sem isso, app não faz nada útil*

### 2️⃣ JWT + Banco de Dados (Confiança)
   *Dados precisam ser persistentes e seguros*

### 3️⃣ Testes + CI/CD (Qualidade)
   *Deploy seguro em produção*

---

Veja [ROADMAP.md](ROADMAP.md) para detalhes completos.
