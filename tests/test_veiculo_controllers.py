"""Testes de controllers/endpoints - cenários HTTP 401/403/409 e payload de erro."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestVeiculoControllersAutenticacao:
    """Testes de autenticação e autorização (401/403)."""
    
    def test_get_veiculos_sem_token_retorna_401(self, client: TestClient):
        """GET /veiculos sem token deve retornar 401."""
        response = client.get("/api/v1/veiculos")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Valida payload de erro
        data = response.json()
        assert "detail" in data
    
    def test_create_veiculo_sem_token_retorna_401(self, client: TestClient):
        """POST /veiculos sem token deve retornar 401."""
        veiculo_data = {
            "placa": "ABC1234",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Prata",
            "preco": 120000.00
        }
        
        response = client.post("/api/v1/veiculos", json=veiculo_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_veiculo_como_user_retorna_403(self, client: TestClient, create_regular_user):
        """POST /veiculos com usuário USER deve retornar 403."""
        headers = {"Authorization": f"Bearer {create_regular_user}"}
        
        veiculo_data = {
            "placa": "ABC1234",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Prata",
            "preco": 120000.00
        }
        
        response = client.post("/api/v1/veiculos", json=veiculo_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Valida payload de erro
        data = response.json()
        assert "detail" in data
        assert "permission" in data["detail"].lower() or "admin" in data["detail"].lower()
    
    def test_update_veiculo_como_user_retorna_403(self, client: TestClient, create_admin_user, create_regular_user):
        """PUT /veiculos/{id} com usuário USER deve retornar 403."""
        admin_headers = {"Authorization": f"Bearer {create_admin_user}"}
        user_headers = {"Authorization": f"Bearer {create_regular_user}"}
        
        # Admin cria veículo
        veiculo_data = {
            "placa": "ABC1234",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Prata",
            "preco": 120000.00
        }
        create_response = client.post("/api/v1/veiculos", json=veiculo_data, headers=admin_headers)
        veiculo_id = create_response.json()["id"]
        
        # USER tenta atualizar
        update_data = {
            "placa": "ABC1234",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Azul",
            "preco": 125000.00
        }
        response = client.put(f"/api/v1/veiculos/{veiculo_id}", json=update_data, headers=user_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_veiculo_como_user_retorna_403(self, client: TestClient, create_admin_user, create_regular_user):
        """DELETE /veiculos/{id} com usuário USER deve retornar 403."""
        admin_headers = {"Authorization": f"Bearer {create_admin_user}"}
        user_headers = {"Authorization": f"Bearer {create_regular_user}"}
        
        # Admin cria veículo
        veiculo_data = {
            "placa": "ABC1234",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Prata",
            "preco": 120000.00
        }
        create_response = client.post("/api/v1/veiculos", json=veiculo_data, headers=admin_headers)
        veiculo_id = create_response.json()["id"]
        
        # USER tenta deletar
        response = client.delete(f"/api/v1/veiculos/{veiculo_id}", headers=user_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestVeiculoControllersConflito:
    """Testes de conflito de dados (409)."""
    
    def test_create_veiculo_placa_duplicada_retorna_409(self, client: TestClient, create_admin_user):
        """POST /veiculos com placa duplicada deve retornar 409."""
        headers = {"Authorization": f"Bearer {create_admin_user}"}
        
        veiculo_data = {
            "placa": "ABC1234",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Prata",
            "preco": 120000.00
        }
        
        # Cria primeiro veículo
        response1 = client.post("/api/v1/veiculos", json=veiculo_data, headers=headers)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Tenta criar segundo com mesma placa
        response2 = client.post("/api/v1/veiculos", json=veiculo_data, headers=headers)
        assert response2.status_code == status.HTTP_409_CONFLICT
        
        # Valida payload de erro
        data = response2.json()
        assert "detail" in data
        assert "placa" in data["detail"].lower()
        assert "ABC1234" in data["detail"]
    
    def test_update_veiculo_para_placa_existente_retorna_409(self, client: TestClient, create_admin_user):
        """PUT /veiculos/{id} com placa já existente deve retornar 409."""
        headers = {"Authorization": f"Bearer {create_admin_user}"}
        
        # Cria dois veículos
        veiculo1_data = {
            "placa": "ABC1234",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Prata",
            "preco": 120000.00
        }
        client.post("/api/v1/veiculos", json=veiculo1_data, headers=headers)
        
        veiculo2_data = {
            "placa": "XYZ5678",
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2023,
            "cor": "Preto",
            "preco": 130000.00
        }
        response2 = client.post("/api/v1/veiculos", json=veiculo2_data, headers=headers)
        veiculo2_id = response2.json()["id"]
        
        # Tenta atualizar veiculo2 para a placa de veiculo1
        update_data = {
            "placa": "ABC1234",  # Placa do veiculo1
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2023,
            "cor": "Preto",
            "preco": 130000.00
        }
        
        response = client.put(f"/api/v1/veiculos/{veiculo2_id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_409_CONFLICT
        
        data = response.json()
        assert "detail" in data
        assert "placa" in data["detail"].lower()
    
    def test_patch_veiculo_para_placa_existente_retorna_409(self, client: TestClient, create_admin_user):
        """PATCH /veiculos/{id} com placa já existente deve retornar 409."""
        headers = {"Authorization": f"Bearer {create_admin_user}"}
        
        # Cria dois veículos
        veiculo1_data = {
            "placa": "ABC1234",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Prata",
            "preco": 120000.00
        }
        client.post("/api/v1/veiculos", json=veiculo1_data, headers=headers)
        
        veiculo2_data = {
            "placa": "XYZ5678",
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2023,
            "cor": "Preto",
            "preco": 130000.00
        }
        response2 = client.post("/api/v1/veiculos", json=veiculo2_data, headers=headers)
        veiculo2_id = response2.json()["id"]
        
        # Tenta fazer patch da placa
        patch_data = {"placa": "ABC1234"}
        
        response = client.patch(f"/api/v1/veiculos/{veiculo2_id}", json=patch_data, headers=headers)
        assert response.status_code == status.HTTP_409_CONFLICT


class TestVeiculoControllersPayloadErro:
    """Testes de payload de erro padronizado."""
    
    def test_erro_404_possui_payload_padronizado(self, client: TestClient, create_regular_user):
        """Erro 404 deve retornar payload com detail."""
        headers = {"Authorization": f"Bearer {create_regular_user}"}
        
        response = client.get("/api/v1/veiculos/9999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert "9999" in str(data["detail"])
    
    def test_erro_validacao_422_possui_payload_padronizado(self, client: TestClient, create_admin_user):
        """Erro de validação 422 deve retornar payload estruturado."""
        headers = {"Authorization": f"Bearer {create_admin_user}"}
        
        # Payload inválido (ano fora do range)
        veiculo_data = {
            "placa": "ABC1234",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 1800,  # Inválido
            "cor": "Prata",
            "preco": 120000.00
        }
        
        response = client.post("/api/v1/veiculos", json=veiculo_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_erro_400_preco_invalido_possui_payload_padronizado(self, client: TestClient, create_regular_user):
        """Erro 400 (minPreco > maxPreco) deve retornar payload com detail."""
        headers = {"Authorization": f"Bearer {create_regular_user}"}
        
        response = client.get("/api/v1/veiculos?minPreco=200000&maxPreco=100000", headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "detail" in data
        assert "preco" in data["detail"].lower() or "min" in data["detail"].lower()
