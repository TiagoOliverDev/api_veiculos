import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Garantir que o settings use .env.test antes de importar a aplicação
os.environ.setdefault("TESTING", "1")

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.user import UserRole

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token():
    """Create an admin token for testing"""
    return create_access_token(data={"sub": "admin", "role": UserRole.ADMIN.value})


@pytest.fixture
def user_token():
    """Create a user token for testing"""
    return create_access_token(data={"sub": "user", "role": UserRole.USER.value})


@pytest.fixture
def create_admin_user(client):
    """Cria um usuário admin via API e devolve o token JWT.

    Parâmetros:
        client (TestClient): Cliente de teste do FastAPI.

    Retorna:
        str: Token de acesso do admin.
    """
    user_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin123",
        "role": UserRole.ADMIN.value
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    return response.json()["access_token"]


@pytest.fixture
def create_regular_user(client):
    """Cria um usuário comum e retorna seu token JWT.

    Parâmetros:
        client (TestClient): Cliente de teste do FastAPI.

    Retorna:
        str: Token de acesso do usuário regular.
    """
    user_data = {
        "username": "user",
        "email": "user@example.com",
        "password": "user123",
        "role": UserRole.USER.value
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": "user",
        "password": "user123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    return response.json()["access_token"]

