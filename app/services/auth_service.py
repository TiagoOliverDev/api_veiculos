from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.core.security import verify_password
from app.models.user import User
from app.core.logging_config import get_logger

logger = get_logger("app.services.auth.AuthService")


class AuthService:
    """Camada de serviço para autenticação e gestão de usuários."""
    
    def __init__(self, db: Session):
        """Inicializa o serviço com o repositório de usuários.

        Parâmetros:
            db (Session): Sessão do SQLAlchemy para operações de usuário.

        Retorna:
            None
        """
        self.repository = UserRepository(db)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Valida credenciais e retorna o usuário quando autenticado.

        Parâmetros:
            username (str): Nome de login.
            password (str): Senha em texto para verificação.

        Retorna:
            Optional[User]: Usuário autenticado se credenciais forem válidas e ativo; caso contrário None.
        """
        user = self.repository.get_by_username(username)
        if not user:
            logger.warning("login falhou: usuario nao encontrado", extra={"username": username})
            return None
        if not verify_password(password, user.hashed_password):
            logger.warning("login falhou: senha invalida", extra={"username": username})
            return None
        if not user.is_active:
            logger.warning("login falhou: usuario inativo", extra={"username": username})
            return None
        logger.info("login bem-sucedido", extra={"username": username, "role": user.role.value})
        return user
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Cria um novo usuário garantindo unicidade de username e email.

        Parâmetros:
            user_data (UserCreate): Dados validados para criação.

        Retorna:
            UserResponse: Representação de saída do usuário recém-criado.
        """
        # Check if username already exists
        existing_user = self.repository.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already registered")
        
        # Check if email already exists
        existing_email = self.repository.get_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already registered")
        
        user = self.repository.create(user_data)
        logger.info(
            "usuario criado", extra={"username": user.username, "email": user.email, "role": user.role.value}
        )
        return UserResponse.model_validate(user)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtém um usuário pelo username.

        Parâmetros:
            username (str): Nome de login.

        Retorna:
            Optional[User]: Usuário encontrado ou None.
        """
        return self.repository.get_by_username(username)
