from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Repositório base com operações CRUD e padrão Repository.

    Parâmetros:
        model (type[ModelType]): Classe ORM que será manipulada.
        db (Session): Sessão do SQLAlchemy para executar operações.

    Retorna:
        BaseRepository: Instância abstrata especializada pelos repositórios concretos.
    """
    
    def __init__(self, model: type[ModelType], db: Session):
        """Inicializa o repositório com modelo e sessão de banco.

        Parâmetros:
            model (type[ModelType]): Classe do modelo SQLAlchemy.
            db (Session): Sessão ativa para operações de persistência.

        Retorna:
            None
        """
        self.model = model
        self.db = db
    
    @abstractmethod
    def get_all(self) -> List[ModelType]:
        """Lista todos os registros do modelo.

        Parâmetros:
            Nenhum.

        Retorna:
            List[ModelType]: Lista com todas as entidades persistidas.
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Busca um registro pelo ID primário.

        Parâmetros:
            id (int): Identificador do registro.

        Retorna:
            Optional[ModelType]: Entidade encontrada ou None se não existir.
        """
        pass
    
    @abstractmethod
    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Cria um novo registro com dados validados.

        Parâmetros:
            obj_in (CreateSchemaType): Dados de criação (pydantic ou dict válido).

        Retorna:
            ModelType: Entidade persistida com ID preenchido.
        """
        pass
    
    @abstractmethod
    def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Atualiza um registro existente.

        Parâmetros:
            id (int): ID do registro a ser atualizado.
            obj_in (UpdateSchemaType): Dados novos para sobrescrever o registro.

        Retorna:
            Optional[ModelType]: Entidade atualizada ou None se não encontrada.
        """
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Remove um registro existente.

        Parâmetros:
            id (int): ID do registro a ser removido.

        Retorna:
            bool: True se removeu, False se o registro não existe.
        """
        pass
