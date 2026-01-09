# Guia de Uso com Docker Compose

## Pré-requisitos

- Docker Desktop instalado
- Docker Compose (incluído no Docker Desktop)

## Configuração Inicial

1. **Copie o arquivo `.env.example` para `.env`:**
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edite o `.env` e ajuste as variáveis conforme sua necessidade:**
   - `DB_PASSWORD`: Altere a senha padrão para uma mais segura
   - `SECRET_KEY`: Use uma chave secreta forte (mude em produção!)
   - `DEBUG`: Defina como `True` para desenvolvimento, `False` para produção

## Iniciando a Aplicação

### Primeira execução (build + start)

```powershell
docker-compose up --build
```

Isso irá:
- Construir a imagem da API
- Iniciar o PostgreSQL (porta 5432)
- Iniciar a API FastAPI (porta 8000)
- Criar o volume `postgres_data` para persistência

### Execuções subsequentes

```powershell
docker-compose up
```

## Parando a Aplicação

```powershell
docker-compose down
```

Para remover também os volumes (banco de dados):

```powershell
docker-compose down -v
```

## Acessando a Aplicação

- **API Swagger**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Visualizando Logs

Em tempo real:
```powershell
docker-compose logs -f api
```

Logs do PostgreSQL:
```powershell
docker-compose logs -f postgres
```

## Executando Testes

Com a aplicação rodando:

```powershell
docker-compose exec api pytest
```

Ou para testes com cobertura:

```powershell
docker-compose exec api pytest --cov=app tests/
```

## Scripts Úteis

### Criar usuário admin via container

```powershell
docker-compose exec api python scripts/create_admin.py
```

### Acessar o banco PostgreSQL direto

```powershell
docker-compose exec postgres psql -U veiculo_user -d veiculos_db
```

## Arquivo de Logs

Os logs da aplicação são salvos em `logs/app.log` (mapeado via volume).

Para visualizar:
```powershell
Get-Content logs/app.log -Tail 50
```

## Diferenças SQLite vs PostgreSQL

| Aspecto | SQLite | PostgreSQL |
|--------|--------|-----------|
| Setup | Simples, arquivo local | Requer container |
| Performance | Leve, desenvolvimento | Robusto, produção |
| Concorrência | Limitada | Excelente |
| Escalabilidade | Pequenos projetos | Grandes projetos |
| Prático para docker | Não | Sim (melhor prática) |

## Troubleshooting

### Erro: "port 5432 is already in use"

A porta do PostgreSQL já está em uso. Modifique em `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"  # Use 5433 no host, 5432 no container
```

Atualize `.env`:
```
DB_PORT=5433
```

### Erro: "connection refused" na API

Aguarde o PostgreSQL iniciar completamente. O `healthcheck` deveria gerenciar isso, mas se necessário:

```powershell
docker-compose up postgres  # Inicie o banco primeiro
docker-compose up api       # Depois a API
```

### Remover tudo e recomeçar do zero

```powershell
docker-compose down -v
docker system prune -a
docker-compose up --build
```

