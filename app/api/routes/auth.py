from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import AuthService
from app.models.user import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Cadastra um novo usuário e retorna seus dados públicos.

    Parâmetros:
        user_data (UserCreate): Dados de entrada contendo username, email, senha e role.
        db (Session): Sessão de banco fornecida pelo FastAPI.

    Retorna:
        UserResponse: Usuário criado sem expor a senha; HTTP 201 em caso de sucesso.
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Realiza login OAuth2 e devolve token JWT para autenticação futura.

    Parâmetros:
        form_data (OAuth2PasswordRequestForm): Dados do formulário com username e password.
        db (Session): Sessão de banco usada para validar credenciais.

    Retorna:
        Token: Dicionário contendo `access_token` e `token_type` em caso de sucesso; 401 se inválido.
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
