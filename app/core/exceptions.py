from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError


class AppException(Exception):
    """Exceção base da aplicação para mapear erros controlados.

    Parâmetros:
        message (str): Mensagem a ser retornada ao cliente.
        status_code (int): Código HTTP associado ao erro.

    Retorna:
        AppException: Instância de exceção personalizada utilizada nos handlers globais.
    """

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Lançada quando um recurso solicitado não é encontrado.

    Parâmetros:
        message (str): Mensagem opcional personalizada.

    Retorna:
        NotFoundException: Erro com status 404 configurado.
    """

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UnauthorizedException(AppException):
    """Lançada quando o usuário não está autenticado.

    Parâmetros:
        message (str): Mensagem opcional personalizada.

    Retorna:
        UnauthorizedException: Erro com status 401 configurado.
    """

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    """Lançada quando o usuário não tem permissão para a ação.

    Parâmetros:
        message (str): Mensagem opcional personalizada.

    Retorna:
        ForbiddenException: Erro com status 403 configurado.
    """

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class BadRequestException(AppException):
    """Lançada para requisições inválidas.

    Parâmetros:
        message (str): Mensagem opcional personalizada.

    Retorna:
        BadRequestException: Erro com status 400 configurado.
    """

    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


async def app_exception_handler(request: Request, exc: AppException):
    """Trata exceções personalizadas da aplicação e retorna JSON padronizado.

    Parâmetros:
        request (Request): Requisição FastAPI recebida.
        exc (AppException): Exceção customizada levantada em alguma rota ou serviço.

    Retorna:
        JSONResponse: Corpo com o erro, mensagem e caminho da requisição usando o status definido.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "path": str(request.url)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Trata erros de validação do FastAPI/Pydantic e detalha campos inválidos.

    Parâmetros:
        request (Request): Requisição com dados inválidos.
        exc (RequestValidationError): Erro de validação contendo a lista de falhas.

    Retorna:
        JSONResponse: Resposta 422 com detalhes dos campos e mensagens de erro.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid request data",
            "details": errors,
            "path": str(request.url)
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Trata exceções do SQLAlchemy devolvendo um erro 500 genérico de banco.

    Parâmetros:
        request (Request): Requisição que causou o erro de banco.
        exc (SQLAlchemyError): Exceção lançada pela camada de persistência.

    Retorna:
        JSONResponse: Resposta 500 informando falha de banco de dados.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "DatabaseError",
            "message": "A database error occurred",
            "path": str(request.url)
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Trata exceções não mapeadas, retornando um erro 500 padrão.

    Parâmetros:
        request (Request): Requisição associada ao erro inesperado.
        exc (Exception): Exceção não tratada.

    Retorna:
        JSONResponse: Resposta 500 com mensagem genérica de erro interno.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "path": str(request.url)
        }
    )
