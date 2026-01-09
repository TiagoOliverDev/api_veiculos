from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)
from app.core.logging_config import setup_logging, get_logger
from app.core.middleware import LoggingMiddleware
from app.api.routes import api_router

# Configure logging (console + arquivo rotativo)
setup_logging(settings)
logger = get_logger("app.main")

# Create database tables (comentado pois será feito nos testes via conftest.py)
# Base.metadata.create_all(bind=engine)

logger.info("API inicializada: montando aplicação")

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API REST para gerenciamento de veículos com autenticação e autorização baseada em roles",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
async def root():
    """Endpoint simples de saúde para indicar que a API está online.

    Parâmetros:
        Nenhum.

    Retorna:
        dict: Status online, mensagem e versão da API.
    """
    return {
        "status": "online",
        "message": "Veículos API is running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint detalhado de saúde que confirma API e banco.

    Parâmetros:
        Nenhum.

    Retorna:
        dict: Indica saúde geral, status do banco e versão da API.
    """
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
