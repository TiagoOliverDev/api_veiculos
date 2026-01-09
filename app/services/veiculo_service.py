from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.veiculo_repository import VeiculoRepository
from app.schemas.veiculo import VeiculoCreate, VeiculoUpdate, VeiculoPatch, VeiculoFilter, VeiculoResponse, VeiculoMarcaReport
from app.models.veiculo import Veiculo
from app.core.logging_config import get_logger

logger = get_logger("app.services.veiculo.VeiculoService")


class VeiculoService:
    """Camada de serviço para regras de negócio de veículos."""
    
    def __init__(self, db: Session):
        """Inicializa o serviço com o repositório de veículos.

        Parâmetros:
            db (Session): Sessão SQLAlchemy ativa.

        Retorna:
            None
        """
        self.repository = VeiculoRepository(db)
    
    def get_all_veiculos(self) -> List[VeiculoResponse]:
        """Lista todos os veículos não deletados.

        Parâmetros:
            Nenhum.

        Retorna:
            List[VeiculoResponse]: Veículos convertidos para schema de resposta.
        """
        veiculos = self.repository.get_all()
        return [VeiculoResponse.model_validate(v) for v in veiculos]
    
    def get_veiculo_by_id(self, veiculo_id: int) -> Optional[VeiculoResponse]:
        """Busca veículo por ID.

        Parâmetros:
            veiculo_id (int): Identificador do veículo.

        Retorna:
            Optional[VeiculoResponse]: Veículo encontrado ou None se não existir.
        """
        veiculo = self.repository.get_by_id(veiculo_id)
        if not veiculo:
            logger.warning("veiculo nao encontrado", extra={"veiculo_id": veiculo_id})
            return None
        return VeiculoResponse.model_validate(veiculo)
    
    def search_veiculos(self, filters: VeiculoFilter) -> List[VeiculoResponse]:
        """Aplica filtros para retornar veículos específicos.

        Parâmetros:
            filters (VeiculoFilter): Campos opcionais de filtro.

        Retorna:
            List[VeiculoResponse]: Veículos que atendem aos filtros.
        """
        veiculos = self.repository.get_with_filters(filters)
        logger.info("busca veiculos com filtros", extra=filters.model_dump(exclude_none=True))
        return [VeiculoResponse.model_validate(v) for v in veiculos]
    
    def create_veiculo(self, veiculo_data: VeiculoCreate) -> VeiculoResponse:
        """Cria um novo veículo e retorna schema de resposta.

        Parâmetros:
            veiculo_data (VeiculoCreate): Dados validados para criação.

        Retorna:
            VeiculoResponse: Veículo criado.
        """
        veiculo = self.repository.create(veiculo_data)
        logger.info("veiculo criado", extra={"veiculo_id": veiculo.id, "marca": veiculo.marca, "modelo": veiculo.modelo})
        return VeiculoResponse.model_validate(veiculo)
    
    def update_veiculo(self, veiculo_id: int, veiculo_data: VeiculoUpdate) -> Optional[VeiculoResponse]:
        """Atualiza totalmente um veículo existente.

        Parâmetros:
            veiculo_id (int): ID do veículo.
            veiculo_data (VeiculoUpdate): Dados completos de atualização.

        Retorna:
            Optional[VeiculoResponse]: Veículo atualizado ou None se não encontrado.
        """
        veiculo = self.repository.update(veiculo_id, veiculo_data)
        if not veiculo:
            logger.warning("veiculo para atualizar nao encontrado", extra={"veiculo_id": veiculo_id})
            return None
        logger.info("veiculo atualizado", extra={"veiculo_id": veiculo.id, "marca": veiculo.marca, "modelo": veiculo.modelo})
        return VeiculoResponse.model_validate(veiculo)
    
    def patch_veiculo(self, veiculo_id: int, veiculo_data: VeiculoPatch) -> Optional[VeiculoResponse]:
        """Atualiza parcialmente um veículo.

        Parâmetros:
            veiculo_id (int): ID do veículo.
            veiculo_data (VeiculoPatch): Campos opcionais para atualização.

        Retorna:
            Optional[VeiculoResponse]: Veículo atualizado ou None se não encontrado.
        """
        veiculo = self.repository.patch(veiculo_id, veiculo_data)
        if not veiculo:
            logger.warning("veiculo para patch nao encontrado", extra={"veiculo_id": veiculo_id})
            return None
        logger.info("veiculo atualizado parcialmente", extra={"veiculo_id": veiculo.id})
        return VeiculoResponse.model_validate(veiculo)
    
    def delete_veiculo(self, veiculo_id: int) -> bool:
        """Remove logicamente um veículo pelo ID.

        Parâmetros:
            veiculo_id (int): Identificador do veículo.

        Retorna:
            bool: True se o veículo foi marcado como deletado; False se não encontrado.
        """
        deleted = self.repository.delete(veiculo_id, soft=True)
        if deleted:
            logger.info("veiculo removido (soft delete)", extra={"veiculo_id": veiculo_id})
        else:
            logger.warning("veiculo para remover nao encontrado", extra={"veiculo_id": veiculo_id})
        return deleted

    def report_por_marca(self) -> List[VeiculoMarcaReport]:
        """Gera relatório de quantidade de veículos agrupados por marca.

        Parâmetros:
            Nenhum.

        Retorna:
            List[VeiculoMarcaReport]: Lista com marca e quantidade.
        """
        rows = self.repository.get_report_by_marca()
        logger.info("relatorio por marca gerado", extra={"marcas": len(rows)})
        return [VeiculoMarcaReport.model_validate(row) for row in rows]
