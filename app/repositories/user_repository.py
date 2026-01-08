from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.base import BaseRepository
from app.core.security import get_password_hash


class UserRepository(BaseRepository[User, UserCreate, None]):
    """Repositório SQLAlchemy para o modelo User."""
    
    def __init__(self, db: Session):
        """Inicializa o repositório com a sessão ativa.

        Parâmetros:
            db (Session): Sessão do SQLAlchemy injetada pela aplicação.

        Retorna:
            None
        """
        super().__init__(User, db)
    
    def get_all(self) -> List[User]:
        """Lista todos os usuários cadastrados.

        Parâmetros:
            Nenhum.

        Retorna:
            List[User]: Lista de usuários.
        """
        return self.db.query(self.model).all()
    
    def get_by_id(self, id: int) -> Optional[User]:
        """Busca usuário pelo ID.

        Parâmetros:
            id (int): ID do usuário.

        Retorna:
            Optional[User]: Usuário encontrado ou None.
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Busca usuário pelo username.

        Parâmetros:
            username (str): Nome de login.

        Retorna:
            Optional[User]: Usuário encontrado ou None.
        """
        return self.db.query(self.model).filter(self.model.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário pelo email.

        Parâmetros:
            email (str): Email do usuário.

        Retorna:
            Optional[User]: Usuário encontrado ou None.
        """
        return self.db.query(self.model).filter(self.model.email == email).first()
    
    def create(self, obj_in: UserCreate) -> User:
        """Cria um novo usuário aplicando hash na senha.

        Parâmetros:
            obj_in (UserCreate): Dados validados para criação do usuário.

        Retorna:
            User: Usuário persistido com hash de senha e ID gerado.
        """
        db_obj = self.model(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            role=obj_in.role
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj_in: None) -> Optional[User]:
        """Atualização não implementada para usuários neste projeto.

        Parâmetros:
            id (int): ID do usuário a atualizar.
            obj_in (None): Placeholder para compatibilidade.

        Retorna:
            Optional[User]: Sempre lança NotImplementedError.
        """
        raise NotImplementedError()
    
    def delete(self, id: int) -> bool:
        """Remove definitivamente um usuário.

        Parâmetros:
            id (int): ID do usuário.

        Retorna:
            bool: True se removido; False se não encontrado.
        """
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
