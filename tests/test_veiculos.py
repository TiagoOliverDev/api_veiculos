import pytest
from fastapi import status


@pytest.fixture
def sample_veiculo():
    """Retorna um payload de veículo padrão para testes.

    Parâmetros:
        Nenhum.

    Retorna:
        dict: Dados de veículo completos para criação em testes.
    """
    return {
        "placa": "ABC1234",
        "marca": "Toyota",
        "modelo": "Corolla",
        "ano": 2023,
        "cor": "Prata",
        "preco": 120000.00,
        "descricao": "Veículo em excelente estado"
    }


@pytest.fixture
def create_admin_user(client):
    """Cria um usuário admin via API e devolve o token JWT.

    Parâmetros:
        client (TestClient): Cliente de teste do FastAPI.

    Retorna:
        str: Token de acesso do admin.
    """
    from app.models.user import UserRole
    
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
    from app.models.user import UserRole
    
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


def test_create_veiculo_as_admin(client, create_admin_user, sample_veiculo):
    """Verifica criação de veículo por usuário admin retorna 201.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_admin_user (str): Token JWT de admin.
        sample_veiculo (dict): Dados de veículo padrão.

    Retorna:
        None: Validação via asserts do status e payload.
    """
    headers = {"Authorization": f"Bearer {create_admin_user}"}
    response = client.post("/api/v1/veiculos", json=sample_veiculo, headers=headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["marca"] == sample_veiculo["marca"]
    assert data["modelo"] == sample_veiculo["modelo"]
    assert "id" in data


def test_create_veiculo_as_user_forbidden(client, create_regular_user, sample_veiculo):
    """Garante que usuário comum recebe 403 ao criar veículo.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_regular_user (str): Token JWT de usuário comum.
        sample_veiculo (dict): Dados de veículo.

    Retorna:
        None: Usa asserts para validar resposta.
    """
    headers = {"Authorization": f"Bearer {create_regular_user}"}
    response = client.post("/api/v1/veiculos", json=sample_veiculo, headers=headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_all_veiculos(client, create_admin_user, create_regular_user, sample_veiculo):
    """Valida listagem de veículos disponível para usuário autenticado.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_admin_user (str): Token de admin para criar veículo.
        create_regular_user (str): Token de usuário para listar.
        sample_veiculo (dict): Dados de veículo base.

    Retorna:
        None: Validação via asserts.
    """
    # Create a veiculo as admin
    admin_headers = {"Authorization": f"Bearer {create_admin_user}"}
    client.post("/api/v1/veiculos", json=sample_veiculo, headers=admin_headers)
    
    # Get all veiculos as regular user
    user_headers = {"Authorization": f"Bearer {create_regular_user}"}
    response = client.get("/api/v1/veiculos", headers=user_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_veiculo_by_id(client, create_admin_user, create_regular_user, sample_veiculo):
    """Confere recuperação de veículo por ID retorna 200 e dados corretos.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_admin_user (str): Token admin para criar.
        create_regular_user (str): Token usuário para leitura.
        sample_veiculo (dict): Dados do veículo.

    Retorna:
        None: Usa asserts para validar.
    """
    # Create a veiculo as admin
    admin_headers = {"Authorization": f"Bearer {create_admin_user}"}
    create_response = client.post("/api/v1/veiculos", json=sample_veiculo, headers=admin_headers)
    veiculo_id = create_response.json()["id"]
    
    # Get veiculo by ID as regular user
    user_headers = {"Authorization": f"Bearer {create_regular_user}"}
    response = client.get(f"/api/v1/veiculos/{veiculo_id}", headers=user_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == veiculo_id
    assert data["marca"] == sample_veiculo["marca"]


def test_get_veiculo_not_found(client, create_regular_user):
    """Garante que buscar veículo inexistente retorna 404.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_regular_user (str): Token do usuário.

    Retorna:
        None: Validação via asserts.
    """
    headers = {"Authorization": f"Bearer {create_regular_user}"}
    response = client.get("/api/v1/veiculos/9999", headers=headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_filter_veiculos_by_marca(client, create_admin_user, create_regular_user):
    """Valida filtro por marca retornando apenas veículos da marca especificada.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_admin_user (str): Token admin para criar veículos.
        create_regular_user (str): Token usuário para consulta.

    Retorna:
        None: Validação via asserts.
    """
    admin_headers = {"Authorization": f"Bearer {create_admin_user}"}
    
    # Create multiple veiculos
    veiculo1 = {
        "placa": "TOY1234",
        "marca": "Toyota",
        "modelo": "Corolla",
        "ano": 2023,
        "cor": "Prata",
        "preco": 120000.00
    }
    veiculo2 = {
        "placa": "HON5678",
        "marca": "Honda",
        "modelo": "Civic",
        "ano": 2023,
        "cor": "Preto",
        "preco": 130000.00
    }
    
    client.post("/api/v1/veiculos", json=veiculo1, headers=admin_headers)
    client.post("/api/v1/veiculos", json=veiculo2, headers=admin_headers)
    
    # Filter by marca
    user_headers = {"Authorization": f"Bearer {create_regular_user}"}
    response = client.get("/api/v1/veiculos?marca=Toyota", headers=user_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["marca"] == "Toyota"


def test_filter_veiculos_by_price_range(client, create_admin_user, create_regular_user):
    """Confere filtro por faixa de preço retorna somente veículos no intervalo.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_admin_user (str): Token admin para criar dados.
        create_regular_user (str): Token usuário para filtrar.

    Retorna:
        None: Usa asserts para validar resultados.
    """
    admin_headers = {"Authorization": f"Bearer {create_admin_user}"}
    
    # Create multiple veiculos with different prices
    veiculo1 = {
        "placa": "CAR1234",
        "marca": "Toyota",
        "modelo": "Corolla",
        "ano": 2023,
        "cor": "Prata",
        "preco": 120000.00
    }
    veiculo2 = {
        "placa": "CAR5678",
        "marca": "Honda",
        "modelo": "Civic",
        "ano": 2023,
        "cor": "Preto",
        "preco": 80000.00
    }
    
    client.post("/api/v1/veiculos", json=veiculo1, headers=admin_headers)
    client.post("/api/v1/veiculos", json=veiculo2, headers=admin_headers)
    
    # Filter by price range
    user_headers = {"Authorization": f"Bearer {create_regular_user}"}
    response = client.get("/api/v1/veiculos?minPreco=100000&maxPreco=150000", headers=user_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["preco"] == 120000.00


def test_update_veiculo_as_admin(client, create_admin_user, sample_veiculo):
    """Garante que admin pode atualizar veículo via PUT e preço é alterado.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_admin_user (str): Token JWT admin.
        sample_veiculo (dict): Dados iniciais do veículo.

    Retorna:
        None: Validação via asserts.
    """
    headers = {"Authorization": f"Bearer {create_admin_user}"}
    
    # Create veiculo
    create_response = client.post("/api/v1/veiculos", json=sample_veiculo, headers=headers)
    veiculo_id = create_response.json()["id"]
    
    # Update veiculo
    updated_data = sample_veiculo.copy()
    updated_data["preco"] = 125000.00
    response = client.put(f"/api/v1/veiculos/{veiculo_id}", json=updated_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["preco"] == 125000.00


def test_patch_veiculo_as_admin(client, create_admin_user, sample_veiculo):
    """Verifica PATCH por admin atualiza campos específicos mantendo os demais.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_admin_user (str): Token admin.
        sample_veiculo (dict): Dados base do veículo.

    Retorna:
        None: Usa asserts para conferir atualização parcial.
    """
    headers = {"Authorization": f"Bearer {create_admin_user}"}
    
    # Create veiculo
    create_response = client.post("/api/v1/veiculos", json=sample_veiculo, headers=headers)
    veiculo_id = create_response.json()["id"]
    
    # Patch veiculo (partial update)
    patch_data = {"preco": 125000.00}
    response = client.patch(f"/api/v1/veiculos/{veiculo_id}", json=patch_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["preco"] == 125000.00
    assert data["marca"] == sample_veiculo["marca"]  # Other fields unchanged


def test_delete_veiculo_as_admin(client, create_admin_user, sample_veiculo):
    """Garante que admin consegue deletar veículo (soft delete) e obtém 204.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_admin_user (str): Token admin.
        sample_veiculo (dict): Dados para criação do veículo.

    Retorna:
        None: Validação via asserts incluindo verificação de 404 após exclusão.
    """
    headers = {"Authorization": f"Bearer {create_admin_user}"}
    
    # Create veiculo
    create_response = client.post("/api/v1/veiculos", json=sample_veiculo, headers=headers)
    veiculo_id = create_response.json()["id"]
    
    # Delete veiculo
    response = client.delete(f"/api/v1/veiculos/{veiculo_id}", headers=headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Try to get deleted veiculo
    get_response = client.get(f"/api/v1/veiculos/{veiculo_id}", headers=headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_veiculo_as_user_forbidden(client, create_admin_user, create_regular_user, sample_veiculo):
    """Confere que usuário comum recebe 403 ao tentar deletar veículo.

    Parâmetros:
        client (TestClient): Cliente de teste.
        create_admin_user (str): Token admin para criar recurso.
        create_regular_user (str): Token usuário para tentativa de exclusão.
        sample_veiculo (dict): Dados do veículo.

    Retorna:
        None: Usa asserts para validar status code.
    """
    admin_headers = {"Authorization": f"Bearer {create_admin_user}"}
    user_headers = {"Authorization": f"Bearer {create_regular_user}"}
    
    # Create veiculo as admin
    create_response = client.post("/api/v1/veiculos", json=sample_veiculo, headers=admin_headers)
    veiculo_id = create_response.json()["id"]
    
    # Try to delete as regular user
    response = client.delete(f"/api/v1/veiculos/{veiculo_id}", headers=user_headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_unauthorized_access(client, sample_veiculo):
    """Valida que endpoints de veículos exigem autenticação (401 sem token).

    Parâmetros:
        client (TestClient): Cliente de teste.
        sample_veiculo (dict): Dados de veículo para tentativa de criação.

    Retorna:
        None: Usa asserts para verificar códigos 401.
    """
    # Try to access without token
    response = client.get("/api/v1/veiculos")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.post("/api/v1/veiculos", json=sample_veiculo)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
