from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Valida uma senha em texto contra um hash armazenado.

    Parâmetros:
        plain_password (str): Senha informada pelo usuário.
        hashed_password (str): Hash bcrypt persistido no banco.

    Retorna:
        bool: True se a senha corresponder ao hash, caso contrário False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera o hash seguro de uma senha usando bcrypt.

    Parâmetros:
        password (str): Senha em texto puro.

    Retorna:
        str: Hash bcrypt resultante para armazenamento seguro.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT de acesso assinado com expiração.

    Parâmetros:
        data (dict): Claims a serem incluídas no token (ex.: sub, role).
        expires_delta (Optional[timedelta]): Tempo de expiração; se omitido usa configuração padrão.

    Retorna:
        str: Token JWT assinado pronto para ser enviado ao cliente.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica e valida um token JWT de acesso.

    Parâmetros:
        token (str): Token JWT recebido no header Authorization.

    Retorna:
        Optional[dict]: Payload do token quando válido; None se inválido ou expirado.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
