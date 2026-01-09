"""Testes unitários para VeiculoRepository - camada de dados."""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.veiculo_repository import VeiculoRepository
from app.schemas.veiculo import VeiculoCreate, VeiculoFilter
from app.models.veiculo import Veiculo


class TestVeiculoRepositoryConstraints:
    """Testes de constraints do banco de dados."""
    
    def test_placa_unica_constraint(self, db_session: Session):
        """Deve garantir constraint de placa única no banco de dados."""
        repo = VeiculoRepository(db_session)
        
        veiculo_data = VeiculoCreate(
            placa="ABC1234",
            marca="Toyota",
            modelo="Corolla",
            ano=2023,
            cor="Prata",
            preco=120000.00
        )
        
        # Cria primeiro veículo
        repo.create(veiculo_data)
        
        # Tenta criar segundo com mesma placa diretamente no banco
        veiculo_duplicado = Veiculo(
            placa="ABC1234",
            marca="Honda",
            modelo="Civic",
            ano=2023,
            cor="Preto",
            preco=130000.00,
            is_deleted=False
        )
        
        db_session.add(veiculo_duplicado)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
    
    def test_get_by_placa_encontra_veiculo(self, db_session: Session):
        """Deve encontrar veículo pela placa."""
        repo = VeiculoRepository(db_session)
        
        veiculo_data = VeiculoCreate(
            placa="ABC1234",
            marca="Toyota",
            modelo="Corolla",
            ano=2023,
            cor="Prata",
            preco=120000.00
        )
        
        created = repo.create(veiculo_data)
        found = repo.get_by_placa("ABC1234")
        
        assert found is not None
        assert found.id == created.id
        assert found.placa == "ABC1234"
    
    def test_get_by_placa_nao_retorna_deletados(self, db_session: Session):
        """Não deve retornar veículo soft-deletado por padrão."""
        repo = VeiculoRepository(db_session)
        
        veiculo_data = VeiculoCreate(
            placa="ABC1234",
            marca="Toyota",
            modelo="Corolla",
            ano=2023,
            cor="Prata",
            preco=120000.00
        )
        
        created = repo.create(veiculo_data)
        repo.delete(created.id, soft=True)
        
        found = repo.get_by_placa("ABC1234")
        assert found is None
        
        # Mas deve encontrar se incluir deletados
        found_with_deleted = repo.get_by_placa("ABC1234", include_deleted=True)
        assert found_with_deleted is not None


class TestVeiculoRepositoryFiltros:
    """Testes de filtros no repositório."""
    
    def test_filtro_marca(self, db_session: Session):
        """Deve filtrar veículos por marca."""
        repo = VeiculoRepository(db_session)
        
        repo.create(VeiculoCreate(
            placa="ABC1234", marca="Toyota", modelo="Corolla",
            ano=2023, cor="Prata", preco=120000.00
        ))
        repo.create(VeiculoCreate(
            placa="XYZ5678", marca="Honda", modelo="Civic",
            ano=2023, cor="Preto", preco=130000.00
        ))
        
        filters = VeiculoFilter(marca="Toyota")
        result = repo.get_with_filters(filters)
        
        assert len(result) == 1
        assert result[0].marca == "Toyota"
    
    def test_filtro_faixa_preco(self, db_session: Session):
        """Deve filtrar veículos por faixa de preço."""
        repo = VeiculoRepository(db_session)
        
        repo.create(VeiculoCreate(
            placa="ABC1234", marca="Toyota", modelo="Corolla",
            ano=2023, cor="Prata", preco=120000.00
        ))
        repo.create(VeiculoCreate(
            placa="XYZ5678", marca="Honda", modelo="Civic",
            ano=2023, cor="Preto", preco=80000.00
        ))
        repo.create(VeiculoCreate(
            placa="DEF9012", marca="Hyundai", modelo="HB20",
            ano=2023, cor="Branco", preco=70000.00
        ))
        
        filters = VeiculoFilter(minPreco=75000, maxPreco=125000)
        result = repo.get_with_filters(filters)
        
        assert len(result) == 2
        placas = [v.placa for v in result]
        assert "ABC1234" in placas
        assert "XYZ5678" in placas
    
    def test_filtro_ano_e_cor(self, db_session: Session):
        """Deve filtrar veículos por ano e cor simultaneamente."""
        repo = VeiculoRepository(db_session)
        
        repo.create(VeiculoCreate(
            placa="ABC1234", marca="Toyota", modelo="Corolla",
            ano=2023, cor="Prata", preco=120000.00
        ))
        repo.create(VeiculoCreate(
            placa="XYZ5678", marca="Toyota", modelo="Hilux",
            ano=2022, cor="Prata", preco=200000.00
        ))
        repo.create(VeiculoCreate(
            placa="DEF9012", marca="Honda", modelo="Civic",
            ano=2023, cor="Preto", preco=130000.00
        ))
        
        filters = VeiculoFilter(ano=2023, cor="Prata")
        result = repo.get_with_filters(filters)
        
        assert len(result) == 1
        assert result[0].placa == "ABC1234"
    
    def test_filtros_nao_incluem_deletados(self, db_session: Session):
        """Filtros não devem retornar veículos soft-deletados."""
        repo = VeiculoRepository(db_session)
        
        created = repo.create(VeiculoCreate(
            placa="ABC1234", marca="Toyota", modelo="Corolla",
            ano=2023, cor="Prata", preco=120000.00
        ))
        
        repo.delete(created.id, soft=True)
        
        filters = VeiculoFilter(marca="Toyota")
        result = repo.get_with_filters(filters)
        
        assert len(result) == 0


class TestVeiculoRepositoryRelatorio:
    """Testes do relatório agregado por marca."""
    
    def test_relatorio_por_marca(self, db_session: Session):
        """Deve retornar contagem agrupada por marca."""
        repo = VeiculoRepository(db_session)
        
        repo.create(VeiculoCreate(
            placa="ABC1234", marca="Toyota", modelo="Corolla",
            ano=2023, cor="Prata", preco=120000.00
        ))
        repo.create(VeiculoCreate(
            placa="XYZ5678", marca="Toyota", modelo="Hilux",
            ano=2023, cor="Branco", preco=200000.00
        ))
        repo.create(VeiculoCreate(
            placa="DEF9012", marca="Honda", modelo="Civic",
            ano=2023, cor="Preto", preco=130000.00
        ))
        
        report = repo.get_report_by_marca()
        
        assert len(report) == 2
        
        # Verifica contagens
        toyota_report = next((r for r in report if r["marca"] == "Toyota"), None)
        honda_report = next((r for r in report if r["marca"] == "Honda"), None)
        
        assert toyota_report is not None
        assert toyota_report["quantidade"] == 2
        assert honda_report is not None
        assert honda_report["quantidade"] == 1
    
    def test_relatorio_exclui_deletados(self, db_session: Session):
        """Relatório não deve incluir veículos soft-deletados."""
        repo = VeiculoRepository(db_session)
        
        v1 = repo.create(VeiculoCreate(
            placa="ABC1234", marca="Toyota", modelo="Corolla",
            ano=2023, cor="Prata", preco=120000.00
        ))
        repo.create(VeiculoCreate(
            placa="XYZ5678", marca="Toyota", modelo="Hilux",
            ano=2023, cor="Branco", preco=200000.00
        ))
        
        # Deleta um veículo
        repo.delete(v1.id, soft=True)
        
        report = repo.get_report_by_marca()
        toyota_report = next((r for r in report if r["marca"] == "Toyota"), None)
        
        assert toyota_report is not None
        assert toyota_report["quantidade"] == 1
