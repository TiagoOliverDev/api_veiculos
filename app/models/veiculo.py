from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.core.database import Base


class Veiculo(Base):
    """Modelo ORM para veículos cadastrados.

    Parâmetros/Colunas:
        id (int): Identificador único auto-incremental.
        placa (str): Placa do veículo (única, obrigatória).
        marca (str): Marca do veículo.
        modelo (str): Modelo do veículo.
        ano (int): Ano de fabricação.
        cor (str): Cor do veículo.
        preco (float): Preço atual.
        descricao (str | None): Descrição opcional.
        is_deleted (bool): Flag de soft delete.
        created_at (datetime): Data de criação.
        updated_at (datetime): Última atualização.
        deleted_at (datetime | None): Momento da exclusão lógica.

    Retorna:
        Veiculo: Instância mapeada pelo SQLAlchemy.
    """
    __tablename__ = "veiculos"
    
    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), unique=True, nullable=False, index=True)
    marca = Column(String(50), nullable=False, index=True)
    modelo = Column(String(100), nullable=False)
    ano = Column(Integer, nullable=False, index=True)
    cor = Column(String(30), nullable=False, index=True)
    preco = Column(Float, nullable=False, index=True)
    descricao = Column(String(500))
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        """Representação curta do veículo para logs e depuração.

        Parâmetros:
            Nenhum.

        Retorna:
            str: String contendo placa, marca e modelo do veículo.
        """
        return f"<Veiculo {self.placa} - {self.marca} {self.modelo}>"
