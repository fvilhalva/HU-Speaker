# Configuração de Ambiente

Este documento explica como configurar as variáveis de ambiente da aplicação HU-Speaker.

## Arquivos de Configuração

- **`.env.example`**: Arquivo de referência com todas as variáveis de ambiente disponíveis. É **seguro compartilhar** este arquivo.
- **`.env`**: Arquivo com as configurações reais (dados sensíveis). **NUNCA COMITAR** - está no .gitignore.

## Setup Inicial

1. **Copie o arquivo de exemplo:**
   ```bash
   cp .env.example .env
   ```

2. **Edite o `.env` com suas configurações:**
   ```bash
   nano .env
   ```

## Variáveis Importantes

### Segurança
- **JWT_SECRET_KEY**: Gere uma chave forte para produção:
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- **ENVIRONMENT**: Use `development` para testes, `production` para produção
- **DEBUG**: Nunca deixe `true` em produção

### Integração Hospitalar (HIS)
- **HIS_API_URL**: URL do seu Sistema de Informação Hospitalar
- **HIS_API_KEY**: Chave de API fornecida pelo HIS

### Email (Notificações)
- **SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD**: Configurações do seu servidor SMTP
- **SMTP_FROM**: Email do remetente das notificações

### Banco de Dados (Opcional)
- **DATABASE_URL**: String de conexão PostgreSQL (quando implementar persistência)

## Ambiente Docker

Em Docker, as variáveis de ambiente são carregadas automaticamente do `.env`:

```bash
docker compose up
```

Para usar um arquivo `.env` específico:
```bash
docker --env-file .env.production up
```

## Em Produção

1. **Gere novas chaves secretas:**
   - JWT_SECRET_KEY
   - Qualquer outro token/senha

2. **Configure com variáveis de ambiente do sistema** (recomendado):
   - Em vez de usar um arquivo `.env`, configure as variáveis no seu orquestrador (Kubernetes, Docker Swarm, etc)
   - Ou use um serviço de secrets (AWS Secrets Manager, Vault, etc)

3. **Use HTTPS** em produção

4. **Certifique-se que apenas o arquivo `.env` é ignorado**, mas `.env.example` é versionado para referência da equipe.

## Segurança

- ✅ `.env.example` → Versionado no Git (exemplos)
- ❌ `.env` → **Nunca** versionado (dados reais)
- ✅ `.env.*.local` → Ignorado (configurações locais)

Ao compartilhar o repositório com a equipe, sempre compartilhe o `.env.example` atualizado, mas **nunca** o `.env` com dados reais.
