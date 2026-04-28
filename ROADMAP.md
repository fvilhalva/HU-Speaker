# 🚀 HU-Speaker - Roadmap

## Status Atual ✅

- ✅ Estrutura modular (MVC/NestJS-like)
- ✅ Docker com Docker Compose
- ✅ Variáveis de ambiente (.env / .env.example)
- ✅ Endpoints básicos (health, root)
- ✅ Testes unitários e integração
- ✅ Config com Pydantic + type safety
- ✅ Documentação de configuração (ENVIRONMENT.md)

---

## 🎯 Fase 1: Funcionalidade Core (CRÍTICO)

**Objetivo**: Tornar a aplicação funcional para o use case principal.

### 1.1 Implementar Síntese de Voz Real (Piper TTS)
- **Localização**: `src/hu_speaker/modules/speaker/service.py`
- **Descrição**: Integrar piper_tts para gerar áudio de verdade
- **Saídas esperadas**: 
  - Arquivos WAV gerados em `AUDIO_OUTPUT_DIR`
  - Endpoint retorna URL/stream do áudio
  - Suporte múltiplos idiomas (pt_BR, es, en)
- **Complexidade**: ⚠️ Média
- **Tempo estimado**: 2-3 dias

### 1.2 Implementar Integração com HIS
- **Localização**: `src/hu_speaker/modules/his/` (novo módulo)
- **Descrição**: CRUD para pacientes/senhas do HIS
- **Endpoints propostos**:
  - `GET /his/patients` - Listar pacientes em fila
  - `POST /his/call-patient` - Chamar paciente e gerar áudio
  - `GET /his/call-records` - Histórico de chamadas
- **Suportar**: MV2k, Tasy, Centaur, APIs genéricas
- **Complexidade**: ⚠️ Média
- **Tempo estimado**: 3-5 dias (depende do HIS)

### 1.3 Adicionar Autenticação JWT
- **Localização**: `src/hu_speaker/modules/auth/` (novo módulo)
- **Descrição**: Login e refresh tokens
- **Endpoints**:
  - `POST /auth/login` - Authenticate user
  - `POST /auth/refresh` - Refresh token
  - `POST /auth/logout` - Logout (opcional)
- **Complexidade**: ✅ Fácil
- **Tempo estimado**: 1 dia
- **Dependências**: `python-jose`, `passlib`

---

## 🗄️ Fase 2: Persistência & Banco de Dados (IMPORTANTE)

**Objetivo**: Adicionar estado persistente à aplicação.

### 2.1 Configurar SQLAlchemy + PostgreSQL
- **Dependências**: `sqlalchemy`, `psycopg2-binary`, `alembic`
- **Criar**:
  - Database connection pool
  - Migration scripts básicas
  - Seed data (usuários teste)
- **Tempo estimado**: 1-2 dias

### 2.2 Implementar ORM Models
- **User** - Usuários do hospital
  - id, username, email, password_hash, role (admin/staff)
  - created_at, updated_at, is_active
- **AudioLog** - Histórico de áudios
  - id, text, language, model_used, file_path
  - duration, size_bytes, created_at
- **CallRecord** - Registro de chamadas
  - id, patient_id, called_at, duration
  - priority, queue_name, created_by
- **Complexidade**: ✅ Fácil
- **Tempo estimado**: 1-2 dias

### 2.3 Adicionar Repositórios/DAOs
- **Padrão**: Repository pattern para abstrair BD
- **Benefícios**: Facilita testes, mudança de BD no futuro
- **Localização**: `src/hu_speaker/infrastructure/repositories/`
- **Tempo estimado**: 1 dia

---

## 📧 Fase 3: Integrações & Notificações (IMPORTANTE)

**Objetivo**: Melhorar confiabilidade e observabilidade.

### 3.1 Implementar Fila de Mensagens (Celery/Redis)
- **Razão**: Síntese de voz pode ser longa, não cabe em request
- **Setup**: Redis (broker) + Celery (worker)
- **Tasks**: `generate_audio`, `send_notification`
- **Docker Compose**: Adicionar redis e celery workers
- **Tempo estimado**: 2-3 dias

### 3.2 Implementar Email/Notificações
- **Localização**: `src/hu_speaker/modules/notifications/`
- **Notificações**:
  - Admins: Erros críticos, síntese falhada
  - Usuários: Áudio pronto para download
- **Provider**: SMTP ou SendGrid
- **Tempo estimado**: 1-2 dias

### 3.3 Logging Estruturado
- **Dependência**: `structlog` ou `python-json-logger`
- **Adicionar**:
  - Request ID tracing (uuid em cada request)
  - Logs JSON estruturados
  - Envio centralizado (ELK Stack, Loki)
- **Localização**: `src/hu_speaker/core/logging.py`
- **Tempo estimado**: 1-2 dias

---

## 🛡️ Fase 4: Segurança & Conformidade (CRÍTICO PARA HOSPITAL)

**Objetivo**: Garantir LGPD/HIPAA compliance.

### 4.1 Implementar Auditoria (LGPD/HIPAA)
- **Modelo AuditLog**:
  - user_id, action, resource_type, resource_id
  - changes_before, changes_after
  - ip_address, user_agent, timestamp
- **Middleware**: Registrar todas as operações
- **Retenção**: Mínimo 1 ano (LGPD)
- **Tempo estimado**: 2 dias

### 4.2 Rate Limiting & Proteção DDOS
- **Dependência**: `slowapi`
- **Limites**:
  - 100 requests/min por IP (público)
  - 1000 requests/min por user (autenticado)
  - 10 síntese/min por usuário
- **Tempo estimado**: 1 dia

### 4.3 Validação e Sanitização de Entrada
- **Implementar**:
  - Validação de comprimento de texto (MAX_TEXT_LENGTH)
  - SQL injection prevention (via ORM)
  - XSS prevention (sanitização output)
- **Tempo estimado**: 1 dia

### 4.4 HTTPS/TLS em Produção
- **Certificados**: Let's Encrypt
- **Setup**: Nginx/Traefik com HTTPS
- **HSTS**: Adicionar headers de segurança
- **Tempo estimado**: 1 dia

---

## 📚 Fase 5: Testes & Qualidade (IMPORTANTE)

**Objetivo**: Garantir confiabilidade antes de produção.

### 5.1 Testes Unitários Completos
- **Target**: 80%+ coverage
- **Mocks**: Piper TTS, HIS API, SMTP
- **Framework**: pytest + pytest-cov
- **Tempo estimado**: 3-5 dias

### 5.2 Testes de Integração
- **E2E**: Requisição completa (login → síntese → salvar)
- **Database**: Usar TestDB (PostgreSQL em container)
- **External APIs**: Usar VCR.py para gravar/reproduzir
- **Tempo estimado**: 2-3 dias

### 5.3 Load Testing
- **Ferramenta**: Apache JMeter ou Locust
- **Cenários**:
  - 100 síntese simultâneas
  - 1000 requests/seg
- **Métricas**: P99 latency, error rate
- **Tempo estimado**: 2 dias

### 5.4 Security Testing
- **OWASP**: Top 10 checklist
- **Dependency scan**: `pip-audit`, `safety`
- **SAST**: `bandit` (static analysis)
- **Tempo estimado**: 1-2 dias

---

## 🚢 Fase 6: Deployment & DevOps (NECESSÁRIO)

**Objetivo**: Preparar para produção.

### 6.1 CI/CD Pipeline
- **Plataforma**: GitHub Actions / GitLab CI
- **Stages**:
  1. Build Docker image
  2. Executar testes
  3. Code quality (ruff, mypy)
  4. Push para registry
  5. Deploy automático
- **Tempo estimado**: 2-3 dias

### 6.2 Docker Multi-stage Build
- **Otimizações**:
  - Separar build stage (compilar deps)
  - Runtime stage (imagem final reduzida)
  - Remover build artifacts
- **Alvo**: Reduzir de 459MB para ~200MB
- **Tempo estimado**: 1 dia

### 6.3 Kubernetes/Orchestração
- **Recursos**:
  - Deployment (app + replicas)
  - Service (exposição)
  - ConfigMap (.env)
  - Secret (senhas, tokens)
  - Ingress (HTTPS, routing)
- **Health checks**: Liveness + readiness probes
- **Tempo estimado**: 3-5 dias

### 6.4 Monitoring & Observabilidade
- **Prometheus**: Coleta de métricas
- **Grafana**: Dashboards
- **ELK/Loki**: Centralização de logs
- **Alertas**: Slack, PagerDuty
- **Tempo estimado**: 3-5 dias

---

## 📖 Fase 7: Documentação (IMPORTANTE)

**Objetivo**: Facilitar onboarding e manutenção.

### 7.1 API Documentation (Swagger)
- **Melhorias**:
  - Descrições detalhadas de endpoints
  - Exemplos de request/response
  - Códigos HTTP documentados
  - Schemas OpenAPI completos
- **Tempo estimado**: 1-2 dias

### 7.2 Developer Guide
- **Conteúdo**:
  - Como adicionar novo módulo
  - Padrões de código (conventions)
  - Guia de contribuição (CONTRIBUTING.md)
  - Troubleshooting comum
- **Tempo estimado**: 1-2 dias

### 7.3 Deployment Guide
- **Conteúdo**:
  - Deployment em produção
  - Configurações de infraestrutura
  - Runbooks de troubleshooting
  - Disaster recovery plan
  - Backup/restore procedures
- **Tempo estimado**: 2-3 dias

---

## ⚡ Quick Wins (Fácil, Impacto Alto)

- [ ] Adicionar `requirements-dev.txt` (para desenvolvimento)
- [ ] Criar script de setup local (`setup.sh`, `setup.ps1`)
- [ ] Adicionar pre-commit hooks (ruff, mypy, bandit)
- [ ] Melhorar README com exemplos práticos
- [ ] Adicionar LICENSE (AGPL v3 para hospital público)
- [ ] Adicionar `.editorconfig` para consistência
- [ ] Documentar ADRs (Architecture Decision Records)
- [ ] Adicionar CHANGELOG.md

---

## 🎯 Prioridade Recomendada

### 1️⃣ IMEDIATO (Sprint 1: ~2 semanas)
- [ ] Implementar Piper TTS real
- [ ] Implementar JWT básico
- [ ] Testes completos (80%+ coverage)
- [ ] Quick wins

**Por quê?** São essenciais para a aplicação funcionar.

### 2️⃣ CURTO PRAZO (Sprint 2-3: ~3-4 semanas)
- [ ] PostgreSQL + SQLAlchemy
- [ ] Integração HIS (ou mock)
- [ ] Logging estruturado
- [ ] Auditoria LGPD
- [ ] CI/CD pipeline

**Por quê?** Necessário antes de produção.

### 3️⃣ MÉDIO PRAZO (Sprint 4-5: ~4-6 semanas)
- [ ] Celery + Redis
- [ ] Rate limiting
- [ ] Email/notificações
- [ ] Documentação completa
- [ ] Load testing

**Por quê?** Melhora confiabilidade e escalabilidade.

### 4️⃣ LONGO PRAZO (Sprint 6+)
- [ ] Kubernetes/orchestração
- [ ] Monitoramento avançado (Prometheus)
- [ ] Performance tuning
- [ ] Multi-tenancy (se necessário)

---

## 📊 Estimativa de Esforço Total

| Fase | Esforço | Duração |
|------|---------|---------|
| 1 (Core) | 20 dias | 3-4 semanas |
| 2 (BD) | 5 dias | 1 semana |
| 3 (Integrações) | 10 dias | 1-2 semanas |
| 4 (Segurança) | 12 dias | 2 semanas |
| 5 (Testes) | 15 dias | 2-3 semanas |
| 6 (DevOps) | 12 dias | 2-3 semanas |
| 7 (Docs) | 8 dias | 1-2 semanas |
| **Total** | **82 dias** | **~4-5 meses** |

*Nota: Pode variar conforme experiência da equipe e complexidade do HIS.*

---

## 🛠️ Tech Stack Recomendado

### Backend
- **Framework**: FastAPI ✅
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Task Queue**: Celery + Redis
- **Auth**: python-jose + passlib

### DevOps
- **Container**: Docker ✅
- **Orchestration**: Kubernetes (Helm)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logs**: ELK Stack ou Loki

### Testing
- **Framework**: pytest
- **Coverage**: pytest-cov
- **Load**: Locust
- **Security**: bandit, pip-audit

---

## 📝 Notas Importantes

### LGPD/HIPAA Compliance
- ✓ Criptografia de dados em repouso
- ✓ HTTPS obrigatório
- ✓ Auditoria de acesso
- ✓ Retenção de 1+ ano
- ✓ Direito ao esquecimento

### Performance
- P99 latency < 2s para síntese
- Suportar 100+ síntese simultâneas
- Cache de modelos TTS

### Resiliência
- Fallback para TTS padrão
- Retry automático com backoff exponencial
- Health checks em todos os serviços
- Backup automático do BD (daily)

---

## 📞 Próximos Passos Imediatos

1. [ ] Revisar e ajustar prioridades conforme contexto do hospital
2. [ ] Criar issues no GitHub com tasks de cada fase
3. [ ] Definir sprints e assign responsáveis
4. [ ] Iniciar Sprint 1 (Piper TTS + JWT + Testes)
5. [ ] Configurar CI/CD pipeline
6. [ ] Agendar reviews semanais

---

**Última atualização**: 2026-04-28  
**Versão**: 1.0
