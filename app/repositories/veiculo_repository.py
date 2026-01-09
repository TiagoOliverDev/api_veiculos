from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.veiculo import Veiculo
from app.schemas.veiculo import VeiculoCreate, VeiculoUpdate, VeiculoPatch, VeiculoFilter
from app.repositories.base import BaseRepository


class VeiculoRepository(BaseRepository[Veiculo, VeiculoCreate, VeiculoUpdate]):
    """Repositório SQLAlchemy para veículos com consultas específicas de negócio."""
    
    def __init__(self, db: Session):
        """Inicializa o repositório com sessão ativa.

        Parâmetros:
            db (Session): Sessão do SQLAlchemy injetada.

        Retorna:
            None
        """
        super().__init__(Veiculo, db)
    
    def get_all(self, include_deleted: bool = False) -> List[Veiculo]:
        """Lista veículos, com opção de incluir registros soft-deletados.

        Parâmetros:
            include_deleted (bool): Quando True retorna também os marcados como deletados.

        Retorna:
            List[Veiculo]: Veículos encontrados conforme filtro de exclusão lógica.
        """
        query = self.db.query(self.model)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        return query.all()
    
    def get_by_id(self, id: int, include_deleted: bool = False) -> Optional[Veiculo]:
        """Busca veículo por ID, opcionalmente incluindo deletados.

        Parâmetros:
            id (int): Identificador do veículo.
            include_deleted (bool): Inclui registros soft-deletados se True.

        Retorna:
            Optional[Veiculo]: Veículo encontrado ou None.
        """
        query = self.db.query(self.model).filter(self.model.id == id)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        return query.first()
    
    def get_with_filters(self, filters: VeiculoFilter) -> List[Veiculo]:
        """Aplica filtros de marca, ano, cor e faixa de preço aos veículos.

        Parâmetros:
            filters (VeiculoFilter): Objeto com campos opcionais para filtragem.

        Retorna:
            List[Veiculo]: Veículos que atendem aos critérios.
        """
        query = self.db.query(self.model).filter(self.model.is_deleted == False)
        
        if filters.marca:
            query = query.filter(self.model.marca == filters.marca)
        
        if filters.ano:
            query = query.filter(self.model.ano == filters.ano)
        
        if filters.cor:
            query = query.filter(self.model.cor == filters.cor)
        
        if filters.min_preco is not None:
            query = query.filter(self.model.preco >= filters.min_preco)
        
        if filters.max_preco is not None:
            query = query.filter(self.model.preco <= filters.max_preco)
        
        return query.all()
    
    def create(self, obj_in: VeiculoCreate) -> Veiculo:
        """Cria um novo veículo persistindo no banco.

        Parâmetros:
            obj_in (VeiculoCreate): Dados de criação validados.

        Retorna:
            Veiculo: Registro criado com ID e timestamps.
        """
        db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj_in: VeiculoUpdate) -> Optional[Veiculo]:
        """Atualiza completamente um veículo existente.

        Parâmetros:
            id (int): ID do veículo a atualizar.
            obj_in (VeiculoUpdate): Dados completos para sobrescrever.

        Retorna:
            Optional[Veiculo]: Veículo atualizado ou None se não encontrado.
        """
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None
        
        update_data = obj_in.model_dump()
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def patch(self, id: int, obj_in: VeiculoPatch) -> Optional[Veiculo]:
        """Atualiza parcialmente um veículo usando apenas campos fornecidos.

        Parâmetros:
            id (int): ID do veículo.
            obj_in (VeiculoPatch): Dados opcionais para atualização parcial.

        Retorna:
            Optional[Veiculo]: Veículo atualizado ou None se não encontrado.
        """
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int, soft: bool = True) -> bool:
        """Remove um veículo, realizando soft delete por padrão.

        Parâmetros:
            id (int): Identificador do veículo.
            soft (bool): Quando True marca como deletado; quando False exclui fisicamente.

        Retorna:
            bool: True se removido (soft ou hard), False se não encontrado.
        """
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False
        
        if soft:
            # Soft delete
            db_obj.is_deleted = True
            db_obj.deleted_at = datetime.utcnow()
            self.db.commit()
        else:
            # Hard delete
            self.db.delete(db_obj)
            self.db.commit()
        
        return True

    def get_report_by_marca(self) -> List[dict]:
        """Retorna quantidade de veículos agrupada por marca (exclui deletados).

        Parâmetros:
            Nenhum.

        Retorna:
            List[dict]: Cada item contém marca e quantidade.
        """
        rows = (
            self.db.query(
                self.model.marca.label("marca"),
                func.count(self.model.id).label("quantidade")
            )
            .filter(self.model.is_deleted == False)
            .group_by(self.model.marca)
            .order_by(self.model.marca.asc())
            .all()
        )
        return [
            {"marca": row.marca, "quantidade": row.quantidade}
            for row in rows
        ]
