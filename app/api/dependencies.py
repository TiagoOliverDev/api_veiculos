from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtém o usuário autenticado a partir do token JWT enviado.

    Parâmetros:
        token (str): Token JWT extraído do header Authorization (Bearer).
        db (Session): Sessão de banco de dados injetada pelo FastAPI.

    Retorna:
        User: Usuário ativo correspondente ao token ou lança HTTPException 401/403.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    auth_service = AuthService(db)
    user = auth_service.get_user_by_username(username)
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Garante que o usuário autenticado está marcado como ativo.

    Parâmetros:
        current_user (User): Usuário retornado por `get_current_user`.

    Retorna:
        User: Mesmo usuário quando ativo ou HTTPException 403 se inativo.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Valida que o usuário autenticado possui papel ADMIN.

    Parâmetros:
        current_user (User): Usuário ativo obtido pela dependência anterior.

    Retorna:
        User: Usuário atual se for admin; caso contrário lança HTTPException 403.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    return current_user
