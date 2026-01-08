from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações carregadas via variáveis de ambiente.

    Parâmetros:
        DATABASE_URL (str): URL de conexão com o banco (ex.: sqlite:///./veiculos.db).
        SECRET_KEY (str): Chave secreta usada para assinar tokens JWT.
        ALGORITHM (str): Algoritmo de assinatura do JWT.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Minutos até expiração do token de acesso.
        API_V1_PREFIX (str): Prefixo raiz das rotas da API.
        PROJECT_NAME (str): Nome exibido na documentação da API.
        DEBUG (bool): Ativa ou não o modo debug e o reload do uvicorn.
        LOG_LEVEL (str): Nível mínimo de log (ex.: DEBUG, INFO, WARNING).
        LOG_FILE (str): Caminho do arquivo de log para gravação persistente.

    Retorna:
        Settings: Instância com as configurações validadas pelo Pydantic.
    """

    # Database
    DATABASE_URL: str = "sqlite:///./veiculos.db"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Veículos API"
    DEBUG: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
