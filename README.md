# HU-Speaker

**HU-Speaker** é uma API de síntese de voz (Text-to-Speech) desenvolvida para o Hospital
Universitário da Grande Dourados (HU-UFGD / Rede Ebserh). Ela usa o motor **Piper TTS** para
transformar texto em áudio de voz natural em português brasileiro.

Seu propósito dentro do hospital é **substituir a chamada verbal de pacientes** ("no grito") por uma
chamada automatizada no painel eletrônico. O caso de uso central é **falar o nome do paciente** —
algo que os painéis de senha comuns não conseguem fazer, pois eles só reproduzem fragmentos de áudio
pré-gravados (letras, números, palavras fixas). O nome de uma pessoa é texto arbitrário e só pode ser
vocalizado por síntese em tempo real.

Este documento descreve a API **e a integração completa** com o NovoSGA e o painel de senhas.

---

## Sumário

- [Visão geral da integração](#visão-geral-da-integração)
- [Arquitetura](#arquitetura)
- [Como funciona a autenticação (JWT)](#como-funciona-a-autenticação-jwt)
- [Endpoints da API](#endpoints-da-api)
- [Passo a passo de execução](#passo-a-passo-de-execução)
- [Configuração (variáveis de ambiente)](#configuração-variáveis-de-ambiente)
- [Velocidade da voz](#velocidade-da-voz)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Solução de problemas](#solução-de-problemas)

---

## Visão geral da integração

A solução é composta por **três serviços independentes** que se comunicam entre si. O HU-Speaker é a
peça de voz; os outros dois já existiam no ecossistema NovoSGA e foram adaptados para conversar com
ele.

| Serviço | O que é | Porta | Tecnologia |
|---|---|---|---|
| **NovoSGA** | Sistema de gestão de senhas/filas | `8081` | PHP 7.2 + PostgreSQL |
| **HU-Speaker** | API de síntese de voz (este projeto) | `8082` | Python 3.11 + FastAPI + Piper |
| **Painel** | Tela de chamada (TV da sala de espera) | `9000` | Web (AngularJS 1.x) |

O fluxo de uma chamada de paciente:

1. No **NovoSGA**, um atendente chama a próxima senha (que carrega o nome do paciente no campo
   `nm_cli`).
2. O **painel** — que consulta o NovoSGA periodicamente — detecta a senha chamada e a exibe na TV.
3. O painel vocaliza a **senha e o local** com áudios pré-gravados (ex.: "senha A, zero, zero, um,
   guichê dois").
4. Em seguida, o painel envia o **nome do paciente** ao **HU-Speaker**, recebe o áudio sintetizado e
   o reproduz (ex.: "João da Silva").

> **Observação:** a integração entre o NovoSGA e o painel é natural — ambos fazem parte do mesmo
> ecossistema NovoSGA. O foco técnico desta documentação é a integração desses dois com o
> **HU-Speaker**, que é o componente novo.

---

## Arquitetura

```
                            ┌──────────────────────────────┐
                            │          NAVEGADOR           │
                            │      (TV da sala de espera)  │
                            │                              │
                            │   Painel de senhas (:9000)   │
                            └──────────────────────────────┘
                                │    ▲             │    ▲
              1. consulta senhas │    │ senha+nome  │    │ 4. áudio (WAV)
                                 ▼    │             ▼    │
        ┌───────────────────────────┐    ┌───────────────────────────────┐
        │        NovoSGA (:8081)     │    │      HU-Speaker (:8082)       │
        │  - filas, senhas, nm_cli   │    │  - POST /speak/synthesize     │
        │  - /api/painel/{unidade}   │    │  - GET  /speak/download/{id}  │
        │  - /painel-token.php  ─────┼───▶│  (valida o JWT assinado com   │
        │    (emite JWT curto)       │ 3. │   o segredo compartilhado)    │
        └───────────────────────────┘token└───────────────────────────────┘
                        │                              ▲
                        │  2. painel pede um token     │
                        └──────────────────────────────┘
                            (segredo JWT compartilhado)
```

Pontos-chave da arquitetura:

- **O áudio é reproduzido no navegador** (a TV), não no servidor.
- **A autenticação é por JWT**, mas o segredo nunca vai para o navegador. O NovoSGA — que é
  server-side — emite tokens curtos que o painel usa.
- Os três serviços rodam em contêineres Docker e compartilham uma **rede Docker externa** chamada
  `sga-net`, o que permite que se enxerguem pelo nome do serviço.

---

## Como funciona a autenticação (JWT)

Todos os endpoints de síntese exigem um **JWT HS256** válido, assinado com o segredo
`JWT_SECRET_KEY` e contendo os claims obrigatórios `sub` e `exp`.

É importante distinguir dois conceitos:

- **`JWT_SECRET_KEY` (o segredo):** uma string fixa, **permanente**, usada para assinar e verificar os
  tokens. Fica **apenas no servidor** (no NovoSGA e no HU-Speaker) e precisa ser **idêntica** nos dois.
  Nunca é enviada ao navegador nem versionada no Git.
- **Token JWT:** gerado a partir do segredo, com validade **curta** (5 minutos). É descartável — se
  vazar, expira rápido.

O painel roda no navegador e **não** pode guardar o segredo. Por isso, ele obtém tokens curtos
dinamicamente:

1. Antes de sintetizar, o painel chama `GET http://localhost:8081/painel-token.php` (no NovoSGA).
2. O NovoSGA assina um JWT de 5 minutos com o `JWT_SECRET_KEY` e o devolve.
3. O painel usa esse token para chamar o HU-Speaker.
4. Quando o token expira, o painel busca outro automaticamente (e trata `401` renovando o token).

Para o áudio (`GET /speak/download/{id}`), o token também é aceito via **query string**
(`?token=<jwt>`), porque o navegador não envia cabeçalhos ao reproduzir áudio por um elemento
`<audio>`.

---

## Endpoints da API

Todos exigem autenticação, exceto o health check.

### `POST /speak/synthesize`
Sintetiza um texto em áudio.

**Cabeçalho:** `Authorization: Bearer <jwt>`
**Corpo (JSON):**
```json
{ "text": "João da Silva", "language": "pt_BR", "length_scale": 1.6, "model": "piper" }
```
- `text` (obrigatório): 1–1000 caracteres.
- `language` (opcional): padrão `"pt_BR"`.
- `length_scale` (opcional): velocidade da fala, 0.5–2.0. Padrão `1.0` (maior = mais devagar).
- `model` (opcional): motor de voz, `"piper"` ou `"kokoro"`. Ausente = `DEFAULT_TTS_MODEL`.

**Resposta:**
```json
{ "id": "798d5acd-...", "text": "João da Silva", "language": "pt_BR", "model": "piper", "status": "completed" }
```
> `model` na resposta é o motor **efetivamente** usado. Se o motor pedido
> falhar, o serviço cai automaticamente para o Piper (fallback) e o campo
> reflete isso.

### `GET /speak/download/{id}`
Devolve o arquivo de áudio WAV (PCM 16-bit, mono, 22050 Hz).
Aceita o token no cabeçalho `Authorization` **ou** na query string `?token=<jwt>`.

### `GET /speak/status/{id}`
Consulta o status de uma síntese.

### `DELETE /speak/{id}`
Remove imediatamente o áudio e seus metadados.

### `GET /health`
Verificação de saúde do serviço. Não requer autenticação.

> Os áudios ficam em um diretório temporário em memória (tmpfs) e são apagados automaticamente após
> ~10 minutos — tempo mais que suficiente para uma chamada de senha.

---

## Passo a passo de execução

O objetivo é subir os três serviços de forma que se comuniquem. Assume-se que os três repositórios
estão em `~/projetos/` (`novosga-HU`, `HU-Speaker`, `novosga-panel-hu`).

### 1. Criar a rede Docker compartilhada (uma única vez)
```bash
docker network create sga-net
```
(se já existir, o comando avisa — pode ignorar.)

### 2. Definir o segredo JWT compartilhado
O NovoSGA e o HU-Speaker precisam do **mesmo** `JWT_SECRET_KEY`.

No **HU-Speaker**, ele fica no `.env`:
```bash
cd ~/projetos/HU-Speaker
cp .env.example .env
# edite o .env e defina um valor forte em JWT_SECRET_KEY
```

No **NovoSGA**, o mesmo valor é fornecido por variável de ambiente (o `docker-compose.yml` do NovoSGA
lê `JWT_SECRET_KEY` do host). A forma mais prática é criar um `.env` na pasta do NovoSGA com o mesmo
valor:
```bash
echo 'JWT_SECRET_KEY=<o-mesmo-segredo-do-hu-speaker>' >> ~/projetos/novosga-HU/.env
```
> **Nunca** versione esse segredo. Garanta que o `.env` está no `.gitignore`.

### 3. Subir o HU-Speaker
```bash
cd ~/projetos/HU-Speaker
docker compose up -d --build
```
Verifique: `curl http://localhost:8082/health` deve responder `{"status":"ok"}`.

### 4. Subir o NovoSGA
```bash
cd ~/projetos/novosga-HU
docker compose up -d
```

### 5. Servir o painel
```bash
cd ~/projetos/novosga-panel-hu
php -S 0.0.0.0:9000
```
Abra `http://localhost:9000` e configure a URL do NovoSGA (`http://localhost:8081`), a unidade, os
serviços e ative a vocalização (incluindo o nome).

### 6. Validar a integração ponta a ponta
```bash
# o NovoSGA emite um token…
TOKEN=$(curl -s http://localhost:8081/painel-token.php | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

# …e o HU-Speaker deve aceitá-lo (esperado: 200)
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8082/speak/synthesize \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"text":"teste","language":"pt_BR"}'
```
Se retornar **200**, os segredos batem e a autenticação está funcionando. Ao chamar uma senha (com
nome preenchido) no NovoSGA, o painel deve falar a senha e, em seguida, o nome do paciente.

---

## Configuração (variáveis de ambiente)

Definidas no `.env` do HU-Speaker (veja `.env.example`):

| Variável | Descrição | Exemplo |
|---|---|---|
| `JWT_SECRET_KEY` | Segredo de assinatura dos tokens (igual ao do NovoSGA) | *(string forte)* |
| `CORS_ORIGINS` | Origens permitidas a chamar a API (inclui o painel) | `http://localhost:9000` |
| `DEFAULT_TTS_MODEL` | Motor usado quando o JSON não traz `model` | `piper` |
| `PIPER_MODEL` | Modelo de voz Piper | `pt_BR-faber-medium.onnx` |
| `KOKORO_LANG_CODE` | Idioma do Kokoro (`p` = pt-BR) | `p` |
| `KOKORO_VOICE` | Voz do Kokoro | `pf_dora` |
| `AUDIO_OUTPUT_DIR` | Diretório temporário dos áudios | `/tmp/hu-speaker-audio` |
| `CLEANUP_TTL_MINUTES` | Minutos até apagar cada áudio | `10` |

### Modelos de voz (engines)

O HU-Speaker suporta múltiplos motores de TTS, selecionáveis por requisição
via o campo `model`:

| Modelo | Motor | Licença | Observação |
|---|---|---|---|
| `piper` | [Piper](https://github.com/rhasspy/piper) | MIT | Rápido e leve, é o motor **base** e o alvo do fallback. |
| `kokoro` | [Kokoro](https://github.com/hexgrad/kokoro) | Apache-2.0 | Qualidade superior, roda em CPU; usa `torch` + `espeak-ng`. |

Adicionar um novo motor é criar uma subclasse de `TTSEngine` em
`modules/speaker/engines/` e registrá-la em `AVAILABLE_MODELS`. Todo o resto
(pré-processamento, WAV, IDs, limpeza) é compartilhado.

> **CORS:** como o painel (`:9000`) e a API (`:8082`) têm origens diferentes, a origem do painel
> precisa estar em `CORS_ORIGINS`, senão o navegador bloqueia a chamada.

---

## Velocidade da voz

O parâmetro `length_scale` ajusta a velocidade da fala (útil para acessibilidade):

| Valor | Efeito |
|---|---|
| `1.0` | Velocidade natural |
| `1.4` | ~40% mais devagar |
| `1.6` | Mais devagar (bom para nomes em ambiente de espera) |
| `2.0` | Bem devagar |

Valores **maiores** deixam a fala **mais lenta**. No painel, esse valor é configurável.

---

## Estrutura do projeto

```
HU-Speaker/
├── src/hu_speaker/
│   ├── app.py                 # cria o app FastAPI (inclui o middleware de CORS)
│   ├── main.py                # ponto de entrada (uvicorn)
│   ├── core/
│   │   ├── config.py          # configurações (env)
│   │   └── security.py        # validação do JWT (header ou ?token=)
│   └── modules/
│       ├── health/            # /health
│       └── speaker/           # síntese, download, status, delete, limpeza
│           └── engines/       # TTSEngine (base) + PiperEngine + KokoroEngine
├── docker-compose.yml         # serviço na rede sga-net, tmpfs para os áudios
├── Dockerfile
└── .env.example
```

---

## Solução de problemas

**O painel não fala o nome, mas fala a senha.**
Abra o console do navegador (F12). As causas mais comuns:
- **CORS** (`blocked by CORS policy`): a origem do painel não está em `CORS_ORIGINS`. Ajuste o `.env`
  do HU-Speaker e reinicie.
- **401**: o `JWT_SECRET_KEY` do NovoSGA e do HU-Speaker estão diferentes. Eles precisam ser idênticos.

**`net::ERR_FAILED` / falha ao chamar o HU-Speaker.**
Verifique se o container está no ar (`curl http://localhost:8082/health`) e se ambos estão na rede
`sga-net`.

**O áudio do nome não toca (mas foi gerado).**
No navegador, a reprodução de áudio automático é bloqueada até haver uma interação do usuário com a
página. Em uma TV real isso não é problema (há uma interação ao configurar o painel).

**O nome sai com pronúncia estranha em siglas coladas a números (ex.: "A001").**
A API já pré-processa esses casos separando letra e dígitos ("A, zero, zero, um"). Nomes de pessoas
não sofrem esse problema.