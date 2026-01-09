"""Teste de integração ponta a ponta (E2E) - fluxo completo da API."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.models.user import UserRole


class TestIntegracaoE2E:
    """Teste end-to-end do fluxo: autenticação → criar → listar/filtrar → detalhar."""
    
    def test_fluxo_completo_admin(self, client: TestClient):
        """Testa fluxo completo de um administrador gerenciando veículos."""
        
        # ===== PASSO 1: Registrar usuário ADMIN =====
        admin_data = {
            "username": "admin_test",
            "email": "admin@test.com",
            "password": "senha_admin_123",
            "role": UserRole.ADMIN.value
        }
        
        register_response = client.post("/api/v1/auth/register", json=admin_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        assert register_response.json()["username"] == "admin_test"
        
        # ===== PASSO 2: Obter token de autenticação =====
        login_data = {
            "username": "admin_test",
            "password": "senha_admin_123"
        }
        
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # ===== PASSO 3: Criar múltiplos veículos =====
        veiculos_para_criar = [
            {
                "placa": "ABC1234",
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2023,
                "cor": "Prata",
                "preco": 120000.00,
                "descricao": "Sedan executivo"
            },
            {
                "placa": "XYZ5678",
                "marca": "Honda",
                "modelo": "Civic",
                "ano": 2023,
                "cor": "Preto",
                "preco": 130000.00,
                "descricao": "Sedan esportivo"
            },
            {
                "placa": "DEF9012",
                "marca": "Toyota",
                "modelo": "Hilux",
                "ano": 2022,
                "cor": "Branco",
                "preco": 200000.00,
                "descricao": "Picape robusta"
            },
            {
                "placa": "GHI3456",
                "marca": "Hyundai",
                "modelo": "HB20",
                "ano": 2023,
                "cor": "Vermelho",
                "preco": 70000.00,
                "descricao": "Hatch compacto"
            }
        ]
        
        veiculos_criados = []
        for veiculo_data in veiculos_para_criar:
            create_response = client.post("/api/v1/veiculos", json=veiculo_data, headers=headers)
            assert create_response.status_code == status.HTTP_201_CREATED
            
            created_veiculo = create_response.json()
            assert created_veiculo["placa"] == veiculo_data["placa"]
            assert created_veiculo["marca"] == veiculo_data["marca"]
            assert "id" in created_veiculo
            assert "created_at" in created_veiculo
            
            veiculos_criados.append(created_veiculo)
        
        # ===== PASSO 4: Listar todos os veículos =====
        list_response = client.get("/api/v1/veiculos", headers=headers)
        assert list_response.status_code == status.HTTP_200_OK
        
        todos_veiculos = list_response.json()
        assert len(todos_veiculos) == 4
        
        # ===== PASSO 5: Filtrar por marca =====
        filtro_marca_response = client.get("/api/v1/veiculos?marca=Toyota", headers=headers)
        assert filtro_marca_response.status_code == status.HTTP_200_OK
        
        veiculos_toyota = filtro_marca_response.json()
        assert len(veiculos_toyota) == 2
        assert all(v["marca"] == "Toyota" for v in veiculos_toyota)
        
        # ===== PASSO 6: Filtrar por faixa de preço =====
        filtro_preco_response = client.get(
            "/api/v1/veiculos?minPreco=100000&maxPreco=150000", 
            headers=headers
        )
        assert filtro_preco_response.status_code == status.HTTP_200_OK
        
        veiculos_faixa = filtro_preco_response.json()
        assert len(veiculos_faixa) == 2  # Corolla e Civic
        assert all(100000 <= v["preco"] <= 150000 for v in veiculos_faixa)
        
        # ===== PASSO 7: Filtrar combinado (marca + ano) =====
        filtro_combinado_response = client.get(
            "/api/v1/veiculos?marca=Toyota&ano=2023",
            headers=headers
        )
        assert filtro_combinado_response.status_code == status.HTTP_200_OK
        
        veiculos_combinado = filtro_combinado_response.json()
        assert len(veiculos_combinado) == 1
        assert veiculos_combinado[0]["placa"] == "ABC1234"
        
        # ===== PASSO 8: Detalhar veículo específico =====
        veiculo_id = veiculos_criados[0]["id"]
        detalhe_response = client.get(f"/api/v1/veiculos/{veiculo_id}", headers=headers)
        assert detalhe_response.status_code == status.HTTP_200_OK
        
        veiculo_detalhado = detalhe_response.json()
        assert veiculo_detalhado["id"] == veiculo_id
        assert veiculo_detalhado["placa"] == "ABC1234"
        assert veiculo_detalhado["descricao"] == "Sedan executivo"
        
        # ===== PASSO 9: Atualizar veículo (PUT) =====
        veiculo_atualizado_data = {
            "placa": "ABC1234",
            "marca": "Toyota",
            "modelo": "Corolla XEI",  # Mudança
            "ano": 2023,
            "cor": "Azul",  # Mudança
            "preco": 125000.00,  # Mudança
            "descricao": "Sedan executivo atualizado"
        }
        
        update_response = client.put(
            f"/api/v1/veiculos/{veiculo_id}",
            json=veiculo_atualizado_data,
            headers=headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        veiculo_apos_update = update_response.json()
        assert veiculo_apos_update["modelo"] == "Corolla XEI"
        assert veiculo_apos_update["cor"] == "Azul"
        assert veiculo_apos_update["preco"] == 125000.00
        
        # ===== PASSO 10: Atualizar parcialmente (PATCH) =====
        patch_data = {"preco": 127000.00}
        
        patch_response = client.patch(
            f"/api/v1/veiculos/{veiculo_id}",
            json=patch_data,
            headers=headers
        )
        assert patch_response.status_code == status.HTTP_200_OK
        
        veiculo_apos_patch = patch_response.json()
        assert veiculo_apos_patch["preco"] == 127000.00
        assert veiculo_apos_patch["modelo"] == "Corolla XEI"  # Não mudou
        
        # ===== PASSO 11: Consultar relatório por marca =====
        relatorio_response = client.get("/api/v1/veiculos/relatorios/por-marca", headers=headers)
        assert relatorio_response.status_code == status.HTTP_200_OK
        
        relatorio = relatorio_response.json()
        assert len(relatorio) == 3  # Toyota, Honda, Hyundai
        
        toyota_report = next((r for r in relatorio if r["marca"] == "Toyota"), None)
        assert toyota_report is not None
        assert toyota_report["quantidade"] == 2
        
        # ===== PASSO 12: Deletar veículo (soft delete) =====
        delete_response = client.delete(f"/api/v1/veiculos/{veiculo_id}", headers=headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # ===== PASSO 13: Confirmar que veículo deletado não aparece nas listagens =====
        list_after_delete = client.get("/api/v1/veiculos", headers=headers)
        veiculos_restantes = list_after_delete.json()
        assert len(veiculos_restantes) == 3
        assert not any(v["id"] == veiculo_id for v in veiculos_restantes)
        
        # ===== PASSO 14: Tentar acessar veículo deletado retorna 404 =====
        get_deleted_response = client.get(f"/api/v1/veiculos/{veiculo_id}", headers=headers)
        assert get_deleted_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_fluxo_user_somente_leitura(self, client: TestClient):
        """Testa que usuário USER consegue apenas ler, não modificar."""
        
        # ===== Criar ADMIN e veículo =====
        admin_data = {
            "username": "admin_setup",
            "email": "admin_setup@test.com",
            "password": "senha123",
            "role": UserRole.ADMIN.value
        }
        client.post("/api/v1/auth/register", json=admin_data)
        
        admin_login = client.post("/api/v1/auth/login", data={
            "username": "admin_setup",
            "password": "senha123"
        })
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        veiculo_data = {
            "placa": "TEST123",
            "marca": "Fiat",
            "modelo": "Uno",
            "ano": 2020,
            "cor": "Branco",
            "preco": 50000.00
        }
        create_resp = client.post("/api/v1/veiculos", json=veiculo_data, headers=admin_headers)
        veiculo_id = create_resp.json()["id"]
        
        # ===== Criar USER =====
        user_data = {
            "username": "user_reader",
            "email": "user@test.com",
            "password": "senha123",
            "role": UserRole.USER.value
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        user_login = client.post("/api/v1/auth/login", data={
            "username": "user_reader",
            "password": "senha123"
        })
        user_token = user_login.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # ===== USER consegue listar =====
        list_response = client.get("/api/v1/veiculos", headers=user_headers)
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.json()) >= 1
        
        # ===== USER consegue detalhar =====
        detail_response = client.get(f"/api/v1/veiculos/{veiculo_id}", headers=user_headers)
        assert detail_response.status_code == status.HTTP_200_OK
        
        # ===== USER consegue ver relatório =====
        report_response = client.get("/api/v1/veiculos/relatorios/por-marca", headers=user_headers)
        assert report_response.status_code == status.HTTP_200_OK
        
        # ===== USER NÃO consegue criar (403) =====
        new_veiculo = {
            "placa": "USER999",
            "marca": "Ford",
            "modelo": "Ka",
            "ano": 2021,
            "cor": "Preto",
            "preco": 45000.00
        }
        create_response = client.post("/api/v1/veiculos", json=new_veiculo, headers=user_headers)
        assert create_response.status_code == status.HTTP_403_FORBIDDEN
        
        # ===== USER NÃO consegue atualizar (403) =====
        update_data = {
            "placa": "TEST123",
            "marca": "Fiat",
            "modelo": "Uno Turbo",
            "ano": 2020,
            "cor": "Branco",
            "preco": 55000.00
        }
        update_response = client.put(f"/api/v1/veiculos/{veiculo_id}", json=update_data, headers=user_headers)
        assert update_response.status_code == status.HTTP_403_FORBIDDEN
        
        # ===== USER NÃO consegue deletar (403) =====
        delete_response = client.delete(f"/api/v1/veiculos/{veiculo_id}", headers=user_headers)
        assert delete_response.status_code == status.HTTP_403_FORBIDDEN
