from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAlchemyEnum
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """Enum que representa os papéis de usuário disponíveis.

    Retorna:
        UserRole: Valor ADMIN ou USER para controle de autorização.
    """

    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    """Modelo ORM para usuários do sistema.

    Parâmetros/Colunas:
        id (int): Identificador único auto-incremental.
        username (str): Nome de login único.
        email (str): Email único do usuário.
        hashed_password (str): Senha armazenada com hash.
        role (UserRole): Papel do usuário (ADMIN ou USER).
        is_active (bool): Flag de usuário ativo.
        created_at (datetime): Data de criação.
        updated_at (datetime): Última atualização.

    Retorna:
        User: Instância persistida pelo SQLAlchemy.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        """Representação amigável do usuário para logs e depuração.

        Parâmetros:
            Nenhum.

        Retorna:
            str: String contendo username e role.
        """
        return f"<User {self.username} ({self.role})>"
