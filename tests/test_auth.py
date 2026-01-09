import pytest
from fastapi import status
from app.models.user import UserRole


def test_health_check(client):
    """Valida que o endpoint /health responde 200 e indica status saudável.

    Parâmetros:
        client (TestClient): Cliente de teste do FastAPI.

    Retorna:
        None: Usa asserts para validar a resposta.
    """
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"


def test_register_user(client):
    """Garante que o registro de usuário retorna 201 e dados corretos.

    Parâmetros:
        client (TestClient): Cliente de teste do FastAPI.

    Retorna:
        None: Validação via asserts da resposta.
    """
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": UserRole.USER.value
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data


def test_register_duplicate_username(client):
    """Confere retorno 400 ao tentar registrar username duplicado.

    Parâmetros:
        client (TestClient): Cliente de teste do FastAPI.

    Retorna:
        None: Usa asserts para verificar o status code.
    """
    user_data = {
        "username": "testuser",
        "email": "test1@example.com",
        "password": "testpassword123",
        "role": UserRole.USER.value
    }
    
    # Register first time
    client.post("/api/v1/auth/register", json=user_data)
    
    # Try to register again with same username
    user_data["email"] = "test2@example.com"
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client):
    """Verifica login bem-sucedido retorna token bearer.

    Parâmetros:
        client (TestClient): Cliente de teste do FastAPI.

    Retorna:
        None: Validação via asserts do token retornado.
    """
    # First register a user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": UserRole.USER.value
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Now login
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Garante que credenciais inválidas resultam em 401.

    Parâmetros:
        client (TestClient): Cliente de teste do FastAPI.

    Retorna:
        None: Validação via asserts.
    """
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
