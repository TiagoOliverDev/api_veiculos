"""Testes unitários para VeiculoService - regras de negócio."""

import pytest
from sqlalchemy.orm import Session
from app.services.veiculo_service import VeiculoService
from app.schemas.veiculo import VeiculoCreate, VeiculoUpdate, VeiculoPatch, VeiculoFilter
from app.models.veiculo import Veiculo


class TestVeiculoServiceDuplicidade:
    """Testes de validação de duplicidade de placa."""
    
    def test_criar_veiculo_com_placa_duplicada_deve_falhar(self, db_session: Session):
        """Deve lançar ValueError ao tentar criar veículo com placa já existente."""
        service = VeiculoService(db_session)
        
        veiculo_data = VeiculoCreate(
            placa="ABC1234",
            marca="Toyota",
            modelo="Corolla",
            ano=2023,
            cor="Prata",
            preco=120000.00
        )
        
        # Cria primeiro veículo
        service.create_veiculo(veiculo_data)
        
        # Tenta criar segundo com mesma placa
        with pytest.raises(ValueError) as exc_info:
            service.create_veiculo(veiculo_data)
        
        assert "placa abc1234" in str(exc_info.value).lower()
    
    def test_atualizar_veiculo_com_placa_de_outro_deve_falhar(self, db_session: Session):
        """Deve lançar ValueError ao tentar atualizar veículo para placa já usada."""
        service = VeiculoService(db_session)
        
        # Cria dois veículos
        veiculo1 = service.create_veiculo(VeiculoCreate(
            placa="ABC1234",
            marca="Toyota",
            modelo="Corolla",
            ano=2023,
            cor="Prata",
            preco=120000.00
        ))
        
        veiculo2 = service.create_veiculo(VeiculoCreate(
            placa="XYZ5678",
            marca="Honda",
            modelo="Civic",
            ano=2023,
            cor="Preto",
            preco=130000.00
        ))
        
        # Tenta atualizar veiculo2 para a placa de veiculo1
        update_data = VeiculoUpdate(
            placa="ABC1234",  # Placa do veiculo1
            marca="Honda",
            modelo="Civic",
            ano=2023,
            cor="Preto",
            preco=130000.00
        )
        
        with pytest.raises(ValueError) as exc_info:
            service.update_veiculo(veiculo2.id, update_data)
        
        assert "placa abc1234" in str(exc_info.value).lower()
    
    def test_patch_veiculo_com_placa_de_outro_deve_falhar(self, db_session: Session):
        """Deve lançar ValueError ao fazer patch com placa já existente."""
        service = VeiculoService(db_session)
        
        veiculo1 = service.create_veiculo(VeiculoCreate(
            placa="ABC1234",
            marca="Toyota",
            modelo="Corolla",
            ano=2023,
            cor="Prata",
            preco=120000.00
        ))
        
        veiculo2 = service.create_veiculo(VeiculoCreate(
            placa="XYZ5678",
            marca="Honda",
            modelo="Civic",
            ano=2023,
            cor="Preto",
            preco=130000.00
        ))
        
        patch_data = VeiculoPatch(placa="ABC1234")
        
        with pytest.raises(ValueError) as exc_info:
            service.patch_veiculo(veiculo2.id, patch_data)
        
        assert "placa abc1234" in str(exc_info.value).lower()


class TestVeiculoServiceFiltros:
    """Testes de filtros combinados."""
    
    def test_filtros_combinados_marca_e_ano(self, db_session: Session):
        """Deve aplicar corretamente filtros de marca e ano juntos."""
        service = VeiculoService(db_session)
        
        # Cria veículos variados
        service.create_veiculo(VeiculoCreate(
            placa="ABC1234", marca="Toyota", modelo="Corolla", 
            ano=2023, cor="Prata", preco=120000.00
        ))
        service.create_veiculo(VeiculoCreate(
            placa="XYZ5678", marca="Toyota", modelo="Hilux", 
            ano=2022, cor="Branco", preco=200000.00
        ))
        service.create_veiculo(VeiculoCreate(
            placa="DEF9012", marca="Honda", modelo="Civic", 
            ano=2023, cor="Preto", preco=130000.00
        ))
        
        # Filtra por marca Toyota e ano 2023
        filters = VeiculoFilter(marca="Toyota", ano=2023)
        result = service.search_veiculos(filters)
        
        assert len(result) == 1
        assert result[0].placa == "ABC1234"
    
    def test_filtros_combinados_cor_e_faixa_preco(self, db_session: Session):
        """Deve aplicar filtros de cor e faixa de preço juntos."""
        service = VeiculoService(db_session)
        
        service.create_veiculo(VeiculoCreate(
            placa="ABC1234", marca="Toyota", modelo="Corolla", 
            ano=2023, cor="Prata", preco=120000.00
        ))
        service.create_veiculo(VeiculoCreate(
            placa="XYZ5678", marca="Honda", modelo="Civic", 
            ano=2023, cor="Prata", preco=80000.00
        ))
        service.create_veiculo(VeiculoCreate(
            placa="DEF9012", marca="Hyundai", modelo="HB20", 
            ano=2023, cor="Preto", preco=70000.00
        ))
        
        # Filtra por cor Prata e preço entre 100k e 150k
        filters = VeiculoFilter(cor="Prata", minPreco=100000, maxPreco=150000)
        result = service.search_veiculos(filters)
        
        assert len(result) == 1
        assert result[0].placa == "ABC1234"
    
    def test_filtros_todos_campos(self, db_session: Session):
        """Deve aplicar todos os filtros simultaneamente."""
        service = VeiculoService(db_session)
        
        service.create_veiculo(VeiculoCreate(
            placa="ABC1234", marca="Toyota", modelo="Corolla", 
            ano=2023, cor="Prata", preco=120000.00
        ))
        service.create_veiculo(VeiculoCreate(
            placa="XYZ5678", marca="Toyota", modelo="Corolla", 
            ano=2023, cor="Branco", preco=120000.00
        ))
        
        filters = VeiculoFilter(
            marca="Toyota", ano=2023, cor="Prata", 
            minPreco=100000, maxPreco=150000
        )
        result = service.search_veiculos(filters)
        
        assert len(result) == 1
        assert result[0].placa == "ABC1234"


class TestVeiculoServiceValidacoes:
    """Testes de validações de PUT/PATCH inválidos."""
    
    def test_put_veiculo_inexistente_retorna_none(self, db_session: Session):
        """PUT em veículo inexistente deve retornar None."""
        service = VeiculoService(db_session)
        
        update_data = VeiculoUpdate(
            placa="ABC1234",
            marca="Toyota",
            modelo="Corolla",
            ano=2023,
            cor="Prata",
            preco=120000.00
        )
        
        result = service.update_veiculo(9999, update_data)
        assert result is None
    
    def test_patch_veiculo_inexistente_retorna_none(self, db_session: Session):
        """PATCH em veículo inexistente deve retornar None."""
        service = VeiculoService(db_session)
        
        patch_data = VeiculoPatch(preco=100000.00)
        result = service.patch_veiculo(9999, patch_data)
        
        assert result is None
    
    def test_patch_veiculo_com_dados_validos(self, db_session: Session):
        """PATCH com dados válidos deve atualizar apenas campos fornecidos."""
        service = VeiculoService(db_session)
        
        veiculo = service.create_veiculo(VeiculoCreate(
            placa="ABC1234",
            marca="Toyota",
            modelo="Corolla",
            ano=2023,
            cor="Prata",
            preco=120000.00
        ))
        
        # Patch apenas do preço
        patch_data = VeiculoPatch(preco=125000.00)
        updated = service.patch_veiculo(veiculo.id, patch_data)
        
        assert updated is not None
        assert updated.preco == 125000.00
        assert updated.marca == "Toyota"  # Não mudou
        assert updated.placa == "ABC1234"  # Não mudou
