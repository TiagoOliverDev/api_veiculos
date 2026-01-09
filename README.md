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
│   ├── api/
│   │   ├── routes/          # Endpoints da API
│   │   │   ├── auth.py      # Rotas de autenticação
│   │   │   └── veiculos.py  # Rotas de veículos
│   │   └── dependencies.py  # Dependências (auth, authorization)
│   ├── core/
│   │   ├── config.py        # Configurações
│   │   ├── database.py      # Setup do banco de dados
│   │   ├── security.py      # JWT e criptografia
│   │   ├── exceptions.py    # Exceções customizadas
│   │   └── middleware.py    # Middleware customizado
│   ├── models/
│   │   ├── user.py          # Model User (SQLAlchemy)
│   │   └── veiculo.py       # Model Veiculo (SQLAlchemy)
│   ├── schemas/
│   │   ├── user.py          # Schemas Pydantic para User
│   │   └── veiculo.py       # Schemas Pydantic para Veiculo
│   ├── repositories/
│   │   ├── base.py          # Repository abstrato
│   │   ├── user_repository.py
│   │   └── veiculo_repository.py
│   ├── services/
│   │   ├── auth_service.py  # Lógica de autenticação
│   │   └── veiculo_service.py # Lógica de negócio de veículos
│   └── main.py              # Aplicação FastAPI
├── tests/
│   ├── conftest.py          # Configuração de testes
│   ├── test_auth.py         # Testes de autenticação
│   └── test_veiculos.py     # Testes de veículos
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validação de dados
- **JWT (PyJWT)** - Autenticação baseada em tokens
- **Pytest** - Framework de testes
- **Uvicorn** - Servidor ASGI

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

```bash
# Copie ou crie o arquivo principal
copy .env.example .env

# Defina no .env (Postgres)
SECRET_KEY=uma-chave-segura-de-32+caracteres
DATABASE_URL=postgresql://usuario:senha@localhost:5432/seu_banco
REDIS_URL=redis://localhost:6379/0
EXCHANGE_RATE_TTL=600

# Opcional: arquivo dedicado de testes (SQLite)
copy .env.example .env.test
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=chave_apenas_para_testes
EXCHANGE_RATE_FIXED=1.0  # evita chamadas externas nos testes
```

Como funciona o carregamento:
- Aplicação normal: lê `.env` (Postgres por padrão no código) e ignora `.env.test`.
- Testes (`pytest`): `tests/conftest.py` força `TESTING=1`, então o `Settings` lê `.env.test` automaticamente e sobrescreve para SQLite. A taxa fixa (`EXCHANGE_RATE_FIXED`) evita chamadas HTTP externas durante os testes.

### 5. Execute a aplicação
```bash
# Modo desenvolvimento
python -m uvicorn app.main:app --reload

# Ou execute diretamente
python app/main.py
```

A API estará disponível em: `http://localhost:8000`

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

## 💵 Preço em USD, câmbio e cache
- O campo `preco` é recebido em BRL e convertido para USD antes de salvar.
- Cotação primária: `https://economia.awesomeapi.com.br/json/last/USD-BRL` (campo `bid`).
- Fallback: `https://api.frankfurter.app/latest?from=USD&to=BRL` (campo `rates.BRL`).
- Cache: usa Redis se `REDIS_URL` estiver configurado; caso contrário, fallback em memória. TTL configurável via `EXCHANGE_RATE_TTL`.
- Em testes, `EXCHANGE_RATE_FIXED=1.0` evita chamadas externas.
- Respostas retornam `preco` já em USD.

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

## 🔒 Segurança

- ✅ Senhas hasheadas com bcrypt
- ✅ JWT para autenticação stateless
- ✅ Validação de entrada em todas as rotas
- ✅ CORS configurável
- ✅ Rate limiting (pode ser adicionado)
- ✅ SQL Injection prevention (SQLAlchemy ORM)

## 🚀 Melhorias Futuras

- [ ] Paginação para listagem de veículos
- [ ] Cache com Redis
- [ ] Rate limiting
- [ ] Docker e Docker Compose
- [ ] CI/CD pipeline
- [ ] Migrations com Alembic
- [ ] Upload de imagens de veículos
- [ ] Logs estruturados (JSON)
- [ ] Monitoramento e métricas

## 📄 Licença

Este projeto foi desenvolvido como parte de um desafio técnico.

---

**Desenvolvido com ❤️ usando FastAPI**