import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.core.logging_config import get_logger

logger = get_logger("app.core.middleware.LoggingMiddleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware que registra método, rota, status e duração das requisições.

    Retorna:
        Response: Resposta original enriquecida com header de tempo de processamento.
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Intercepta a requisição para registrar logs antes e depois do processamento.

        Parâmetros:
            request (Request): Requisição HTTP recebida pelo FastAPI.
            call_next (Callable): Função que encaminha a requisição para a próxima camada.

        Retorna:
            Response: Resposta produzida pela aplicação com cabeçalho de duração.
        """
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Duration: {duration:.3f}s"
        )
        
        # Add custom header with duration
        response.headers["X-Process-Time"] = str(duration)
        
        return response


class CORSMiddleware:
    """Placeholder para configuração customizada de CORS.

    Parâmetros:
        Nenhum.

    Retorna:
        None: Classe vazia, mantida por compatibilidade/possível extensão futura.
    """
    pass
