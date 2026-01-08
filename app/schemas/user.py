from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    """Dados básicos de usuário compartilhados entre schemas.

    Parâmetros:
        username (str): Nome de login entre 3 e 50 caracteres.
        email (EmailStr): Email válido do usuário.

    Retorna:
        UserBase: Objeto Pydantic validado com os campos principais.
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Payload para criação de usuário.

    Parâmetros:
        password (str): Senha mínima de 6 caracteres.
        role (UserRole): Papel atribuído ao usuário.

    Retorna:
        UserCreate: Objeto validado para persistência.
    """
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER


class UserResponse(UserBase):
    """Schema de saída para exibição de usuário.

    Parâmetros:
        id (int): Identificador do usuário.
        role (UserRole): Papel do usuário.
        is_active (bool): Status de atividade.

    Retorna:
        UserResponse: Objeto pronto para serialização na API.
    """
    id: int
    role: UserRole
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Representa o token JWT retornado no login.

    Parâmetros:
        access_token (str): Token JWT assinado.
        token_type (str): Tipo do token, padrão "bearer".

    Retorna:
        Token: Objeto serializável com dados do token.
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Dados decodificados do token usados na aplicação.

    Parâmetros:
        username (str | None): Username presente no claim `sub`.
        role (UserRole | None): Papel do usuário.

    Retorna:
        TokenData: Dados opcionais extraídos do token JWT.
    """
    username: Optional[str] = None
    role: Optional[UserRole] = None
