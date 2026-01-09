# API de Gerenciamento de Veículos

API REST desenvolvida com **FastAPI** para gerenciamento de veículos, com autenticação JWT e controle de acesso baseado em roles (RBAC).

## 🏗️ Arquitetura do Projeto

Este projeto implementa uma **Arquitetura em Camadas (Layered Architecture)** combinada com os padrões:
- **Repository Pattern** para abstração de dados
- **Service Layer Pattern** para lógica de negócio
- **Dependency Injection** nativo do FastAPI
- **Clean Architecture principles**

### 📂 Estrutura de Diretórios

```
projeto/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Aplicação FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py          # Dependências (auth, authorization)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py              # Rotas de autenticação
│   │       └── veiculos.py          # Rotas de veículos
│   ├── core/
│   │   ├── __init__.py
│   │   ├── cache.py                 # Sistema de cache Redis/memória
│   │   ├── config.py                # Configurações e Settings
│   │   ├── database.py              # Setup do banco de dados
│   │   ├── exceptions.py            # Exception handlers
│   │   ├── logging_config.py        # Configuração de logs rotativos
│   │   ├── middleware.py            # Middleware de logging
│   │   └── security.py              # JWT e criptografia
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                  # Model User (SQLAlchemy)
│   │   └── veiculo.py               # Model Veiculo (SQLAlchemy)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                  # Repository abstrato
│   │   ├── user_repository.py       # Repositório de usuários
│   │   └── veiculo_repository.py    # Repositório de veículos
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                  # Schemas Pydantic para User
│   │   └── veiculo.py               # Schemas Pydantic para Veiculo
│   └── services/
│       ├── __init__.py
│       ├── auth_service.py          # Lógica de autenticação
│       ├── exchange_service.py      # Serviço de câmbio USD/BRL
│       └── veiculo_service.py       # Lógica de negócio de veículos
├── scripts/
│   ├── __init__.py
│   └── create_admin.py              # Script para criar usuário admin
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Configuração e fixtures de testes
│   ├── test_auth.py                 # Testes de autenticação
│   ├── test_integration_e2e.py      # Testes de integração E2E
│   ├── test_veiculo_controllers.py  # Testes de controllers HTTP
│   ├── test_veiculo_repository.py   # Testes de repositório
│   ├── test_veiculo_service.py      # Testes de service layer
│   └── test_veiculos.py             # Testes gerais de veículos
├── .env                             # Variáveis de ambiente (produção)
├── .env.example                     # Template de configuração
├── .env.test                        # Variáveis de ambiente para testes
├── .gitignore
├── ARCHITECTURE.md                  # Documentação de arquitetura
├── ATENDIMENTO_REQUISITOS.md        # Relatório de requisitos atendidos
├── docker-compose.yml               # Compose: Postgres + Redis + API
├── Dockerfile                       # Imagem Docker da API
├── pytest.ini                       # Configuração do pytest
├── README.md                        # Documentação principal
└── requirements.txt                 # Dependências Python
```

## 🚀 Tecnologias Utilizadas

- **FastAPI 0.109.0** - Framework web moderno e rápido
- **SQLAlchemy 2.0.25** - ORM para Python
- **PostgreSQL 16** - Banco de dados relacional (produção)
- **Redis 7** - Cache in-memory para cotações de câmbio
- **Pydantic 2.x** - Validação de dados
- **JWT (python-jose)** - Autenticação baseada em tokens
- **bcrypt 3.2.2** - Hash de senhas
- **Pytest 7.4.4** - Framework de testes
- **Uvicorn** - Servidor ASGI
- **Docker & Docker Compose** - Containerização

## 📋 Requisitos

- Python 3.8+
- pip

## ⚙️ Configuração e Instalação

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd projeto
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
Use Postgres em desenvolvimento/produção e SQLite apenas para testes automatizados.

**Arquivo `.env` (Produção/Desenvolvimento):**
```bash
# Copie o template
copy .env.example .env

# Configurações obrigatórias
SECRET_KEY=uma-chave-segura-de-32+caracteres-minimo
DATABASE_URL=postgresql://usuario:senha@localhost:5432/seu_banco

# Redis (cache de cotação USD/BRL) - OBRIGATÓRIO para produção
REDIS_URL=redis://localhost:6379/0
EXCHANGE_RATE_TTL=600  # Tempo de cache em segundos (10 minutos)

# Opcional: fixar taxa de câmbio (apenas dev/testes)
# EXCHANGE_RATE_FIXED=5.0
```

**Arquivo `.env.test` (Testes Automatizados):**
```bash
# Copie o template
copy .env.example .env.test

# Configurações de teste
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=chave_apenas_para_testes_nao_usar_em_producao
TESTING=1

# Evita chamadas externas durante testes
EXCHANGE_RATE_FIXED=1.0

# Redis opcional em testes (usa fallback em memória)
REDIS_URL=redis://localhost:6379/1
```

Como funciona o carregamento:
- Aplicação normal: lê `.env` (Postgres por padrão no código) e ignora `.env.test`.
- Testes (`pytest`): `tests/conftest.py` força `TESTING=1`, então o `Settings` lê `.env.test` automaticamente e sobrescreve para SQLite. A taxa fixa (`EXCHANGE_RATE_FIXED`) evita chamadas HTTP externas durante os testes.

### 5b. Execute a aplicação

**Desenvolvimento local (sem Docker):**
```bash
# Certifique-se de ter Postgres e Redis rodando
python -m uvicorn app.main:app --reload

# Ou execute diretamente
python app/main.py
```

**Produção com Docker Compose (RECOMENDADO):**
```bash
# Inicia todos os serviços
docker-compose up -d --build

# Ver logs
docker-compose logs -f api

# Parar serviços
docker-compose down
```

A API estará disponível em: `http://localhost:8000`

### 5a. Subir Redis para cache de câmbio

**Opção 1: Container Docker standalone**
```bash
docker run --name redis -p 6379:6379 -d redis:7-alpine
```

**Opção 2: Docker Compose (RECOMENDADO)**
```bash
# Sobe Postgres + Redis + API juntos
docker-compose up -d --build
```

O `docker-compose.yml` já está configurado com:
- **PostgreSQL 16** na porta 5432
- **Redis 7** na porta 6379  
- **API FastAPI** na porta 8000
- Rede interna `veiculo_network` para comunicação entre serviços
- Health checks para garantir disponibilidade

**Por que Redis é importante?**
- ✅ Cacheia a cotação USD/BRL por 10 minutos (configurável)
- ✅ Reduz chamadas às APIs externas de câmbio
- ✅ Melhora performance em operações com múltiplos veículos
- ✅ Fallback automático para cache em memória se Redis estiver indisponível

**Configuração no `.env`:**
```env
REDIS_URL=redis://localhost:6379/0  # Standalone
# ou
REDIS_URL=redis://redis:6379/0      # Docker Compose (nome do service)
EXCHANGE_RATE_TTL=600                # 10 minutos de cache
```

## 📚 Documentação da API

Após iniciar a aplicação, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Autenticação

A API usa **JWT (JSON Web Tokens)** para autenticação. 

### Fluxo de Autenticação:

1. **Registrar usuário**: `POST /api/v1/auth/register`
2. **Fazer login**: `POST /api/v1/auth/login` → retorna access_token
3. **Usar token**: Adicionar header `Authorization: Bearer {access_token}` nas requisições

### Roles (Papéis):
- **USER**: Pode apenas visualizar veículos
- **ADMIN**: Pode criar, atualizar e deletar veículos

## 💵 Preço em USD, Câmbio e Cache

### Como funciona a conversão de preço?

1. **Entrada:** Cliente envia `preco` em **BRL** (Reais)
2. **Conversão:** Sistema busca cotação USD/BRL em tempo real
3. **Armazenamento:** Salva no banco de dados em **USD** (Dólar)
4. **Resposta:** API retorna `preco` em **USD**

### APIs de Câmbio (com fallback automático)

| Prioridade | API | Endpoint | Campo usado |
|------------|-----|----------|-------------|
| **1ª** | AwesomeAPI | `https://economia.awesomeapi.com.br/json/last/USD-BRL` | `USDBRL.bid` |
| **2ª** | Frankfurter | `https://api.frankfurter.app/latest?from=USD&to=BRL` | `rates.BRL` |

Se a AwesomeAPI falhar (timeout, erro HTTP), o sistema tenta automaticamente a Frankfurter.

### Sistema de Cache com Redis

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │ POST /veiculos {preco: 100000 BRL}
       ▼
┌─────────────────────┐
│  VeiculoService     │
│  _convert_to_usd()  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐     Cache HIT?
│  ExchangeService    │────────Yes────► Retorna taxa do Redis
│  get_usd_brl_rate() │                (TTL: 10min)
└──────┬──────────────┘
       │ Cache MISS
       ▼
┌─────────────────────┐
│  AwesomeAPI         │────Sucesso────► Salva no Redis + Retorna
│  (Primária)         │
└──────┬──────────────┘
       │ Falha
       ▼
┌─────────────────────┐
│  Frankfurter        │────Sucesso────► Salva no Redis + Retorna
│  (Fallback)         │
└──────┬──────────────┘
       │ Falha
       ▼
   Exceção HTTPException 503
```

### Configurações

```env
# Redis (produção)
REDIS_URL=redis://redis:6379/0
EXCHANGE_RATE_TTL=600  # Cache por 10 minutos

# Testes (evita chamadas externas)
EXCHANGE_RATE_FIXED=1.0  # Taxa fixa para testes
```

### Comportamento de Fallback

- ✅ **Redis disponível:** Cache funciona normalmente (rápido)
- ⚠️ **Redis indisponível:** Usa cache em memória local (ainda funciona)
- ⚠️ **APIs de câmbio falham:** Retorna HTTP 503 (Service Unavailable)
- ✅ **Testes:** Usa `EXCHANGE_RATE_FIXED=1.0` (sem chamadas HTTP)

## 🗑️ Soft delete
- `DELETE /api/v1/veiculos/{id}` marca o registro como `ativo=false` e `is_deleted=true`.
- Listagens e filtros retornam apenas veículos ativos (não deletados).

## 🛣️ Endpoints

### Autenticação

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/v1/auth/register` | Registrar novo usuário | Não |
| POST | `/api/v1/auth/login` | Fazer login | Não |

### Veículos

| Método | Endpoint | Descrição | Auth | Role |
|--------|----------|-----------|------|------|
| GET | `/api/v1/veiculos` | Listar veículos (suporta filtros combinados) | Sim | USER/ADMIN |
| GET | `/api/v1/veiculos?marca={marca}` | Filtrar por marca | Sim | USER/ADMIN |
| GET | `/api/v1/veiculos?ano={ano}` | Filtrar por ano | Sim | USER/ADMIN |
| GET | `/api/v1/veiculos?cor={cor}` | Filtrar por cor | Sim | USER/ADMIN |
| GET | `/api/v1/veiculos?minPreco={min}&maxPreco={max}` | Filtrar por faixa de preço | Sim | USER/ADMIN |
| GET | `/api/v1/veiculos/relatorios/por-marca` | Relatório de quantidade por marca | Sim | USER/ADMIN |
| GET | `/api/v1/veiculos/{id}` | Obter veículo por ID | Sim | USER/ADMIN |
| POST | `/api/v1/veiculos` | Criar novo veículo | Sim | **ADMIN** |
| PUT | `/api/v1/veiculos/{id}` | Atualizar veículo (completo) | Sim | **ADMIN** |
| PATCH | `/api/v1/veiculos/{id}` | Atualizar veículo (parcial) | Sim | **ADMIN** |
| DELETE | `/api/v1/veiculos/{id}` | Deletar veículo (soft delete) | Sim | **ADMIN** |

Paginação e ordenação em `/api/v1/veiculos`:
- `page` (default 1), `pageSize` (default 10, max 100)
- `sortBy` (created_at, updated_at, preco, ano, marca), `sortOrder` (asc|desc)

## 🧪 Testes

Fluxo padrão (usa SQLite com `.env.test` automaticamente):

```bash
# Todos os testes (usa TESTING=1 e carrega .env.test)
pytest

# Com cobertura
pytest --cov=app

# Testes específicos
pytest tests/test_auth.py -v
pytest tests/test_veiculo_service.py -v
pytest tests/test_veiculo_repository.py -v
pytest tests/test_veiculo_controllers.py -v
pytest tests/test_integration_e2e.py -v
```

Observações:
- O `conftest.py` define `TESTING=1` antes de importar a aplicação, então o `Settings` lê `.env.test` e usa SQLite (`DATABASE_URL=sqlite:///./test.db`).
- O `get_db` é sobrescrito nos testes para apontar para o engine de teste e criar/derrubar as tabelas a cada função (`scope="function"`).
- Em execução normal (sem `TESTING=1`), o default volta a ser Postgres; garanta que `DATABASE_URL` esteja definido no `.env` ou via variável de ambiente.
- Para evitar chamadas externas nas suítes, mantenha `EXCHANGE_RATE_FIXED=1.0` no `.env.test`.

## 🏛️ Padrões de Design Implementados

### 1. **Layered Architecture (Arquitetura em Camadas)**
- **Presentation Layer**: Routers (API endpoints)
- **Service Layer**: Lógica de negócio
- **Data Access Layer**: Repositories
- **Domain Layer**: Models e Schemas

### 2. **Repository Pattern**
- Abstração do acesso a dados
- Facilita testes e manutenção
- Permite trocar a fonte de dados sem afetar outras camadas

### 3. **Service Layer Pattern**
- Encapsula a lógica de negócio
- Orquestra operações entre repositories
- Mantém controllers (routers) leves

### 4. **Dependency Injection**
- FastAPI fornece DI nativo
- Facilita testes e desacoplamento
- Usado para database sessions, autenticação, etc.

### 5. **DTO Pattern (Data Transfer Objects)**
- Schemas Pydantic para validação
- Separação entre dados de entrada, saída e domínio
- Validação automática

## ✨ Boas Práticas Implementadas

✅ **Validação de Dados**: Schemas Pydantic com validações rigorosas  
✅ **Tratamento de Erros**: Exception handlers customizados  
✅ **Soft Delete**: Veículos não são removidos fisicamente do banco  
✅ **Segurança**: JWT, bcrypt para senhas, RBAC  
✅ **Testes Automatizados**: Cobertura de casos de uso principais  
✅ **Documentação Automática**: Swagger/OpenAPI  
✅ **Logging**: Middleware para logs de requisições  
✅ **Configuração por Ambiente**: Usando variáveis de ambiente  
✅ **Type Hints**: Código totalmente tipado  
✅ **Separação de Responsabilidades**: Código organizado e modular  

## 🔄 Fluxo de Requisição

```
Request → Router → Dependencies (Auth) → Service → Repository → Database
                                           ↓
Response ← Router ← Exception Handler ← Service ← Repository ← Database
```

## 📝 Exemplo de Uso

### 1. Registrar um Admin
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "role": "ADMIN"
  }'
```

### 2. Fazer Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 3. Criar um Veículo
```bash
curl -X POST "http://localhost:8000/api/v1/veiculos" \
  -H "Authorization: Bearer {seu_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "marca": "Toyota",
    "modelo": "Corolla",
    "ano": 2023,
    "cor": "Prata",
    "preco": 120000.00,
    "descricao": "Veículo em excelente estado"
  }'
```

### 4. Buscar Veículos por Filtro
```bash
curl -X GET "http://localhost:8000/api/v1/veiculos?marca=Toyota&minPreco=100000&maxPreco=150000" \
  -H "Authorization: Bearer {seu_token}"
```

## � Docker e Docker Compose

### Estrutura do docker-compose.yml

O projeto inclui configuração completa para rodar todos os serviços:

```yaml
services:
  postgres:   # Banco de dados PostgreSQL 16
  redis:      # Cache Redis 7
  api:        # API FastAPI
```

### Comandos Úteis

```bash
# Iniciar todos os serviços
docker-compose up -d --build

# Ver logs em tempo real
docker-compose logs -f

# Ver logs apenas da API
docker-compose logs -f api

# Parar serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados!)
docker-compose down -v

# Reiniciar apenas um serviço
docker-compose restart api

# Verificar status dos serviços
docker-compose ps

# Executar comando dentro do container da API
docker-compose exec api python scripts/create_admin.py

# Acessar shell do container
docker-compose exec api bash
```

### Portas Expostas

| Serviço | Porta Interna | Porta Host |
|---------|---------------|------------|
| API (FastAPI) | 8000 | 8000 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |

### Variáveis de Ambiente no Docker

O `docker-compose.yml` injeta variáveis do arquivo `.env` automaticamente:
- `DATABASE_URL` → Aponta para `postgres:5432` (nome do service)
- `REDIS_URL` → Aponta para `redis://redis:6379/0`
- `SECRET_KEY`, `EXCHANGE_RATE_TTL` → Vêm do `.env`

## 🔒 Segurança

- ✅ Senhas hasheadas com **bcrypt 3.2.2**
- ✅ **JWT** para autenticação stateless (python-jose)
- ✅ Validação de entrada em todas as rotas (**Pydantic**)
- ✅ **RBAC** (Role-Based Access Control): USER vs ADMIN
- ✅ **CORS** configurável (middleware FastAPI)
- ✅ **SQL Injection prevention** (SQLAlchemy ORM com parametrização)
- ✅ **Soft delete** (dados nunca são apagados fisicamente)
- ✅ **Logs de auditoria** em todas as requisições (middleware)
- ✅ **Type hints** completos (validação estática com mypy)

## 🚀 Melhorias Futuras

### Já Implementado ✅
- ✅ Paginação e ordenação em listagens
- ✅ Cache com Redis (fallback em memória)
- ✅ Docker e Docker Compose
- ✅ Logs rotativos com configuração centralizada
- ✅ Soft delete com flags `ativo` e `is_deleted`
- ✅ Conversão de preço BRL → USD com APIs externas
- ✅ Dual API fallback (AwesomeAPI → Frankfurter)
- ✅ Documentação OpenAPI/Swagger completa
- ✅ 48 testes automatizados (cobertura > 75%)

### Roadmap 🗺️
- [ ] **Rate limiting** (proteção contra abuso de API)
- [ ] **CI/CD pipeline** (GitHub Actions / GitLab CI)
- [ ] **Migrations com Alembic** (versionamento de schema)
- [ ] **Upload de imagens** de veículos (S3/MinIO)
- [ ] **Logs estruturados JSON** (melhor integração com ELK/Datadog)
- [ ] **Monitoramento e métricas** (Prometheus + Grafana)
- [ ] **Health checks** avançados (verificar Redis, Postgres, APIs externas)
- [ ] **Webhooks** para notificações de eventos
- [ ] **GraphQL** como alternativa ao REST
- [ ] **Testes de carga** (Locust/K6)

## 📄 Licença

Este projeto foi desenvolvido como parte de um desafio técnico.

---

**Desenvolvido usando FastAPI**