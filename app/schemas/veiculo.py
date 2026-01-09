from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class VeiculoBase(BaseModel):
    """Campos básicos compartilhados entre operações de veículo.

    Parâmetros:
        placa (str): Placa do veículo (formato brasileiro ou internacional).
        marca (str): Marca do veículo.
        modelo (str): Modelo do veículo.
        ano (int): Ano de fabricação (1900-2100).
        cor (str): Cor.
        preco (float): Preço maior que zero.
        descricao (str | None): Descrição opcional.

    Retorna:
        VeiculoBase: Objeto validado com os campos principais de veículo.
    """
    placa: str = Field(..., min_length=7, max_length=10, description="Placa do veículo")
    marca: str = Field(..., min_length=1, max_length=50, description="Marca do veículo")
    modelo: str = Field(..., min_length=1, max_length=100, description="Modelo do veículo")
    ano: int = Field(..., ge=1900, le=2100, description="Ano de fabricação")
    cor: str = Field(..., min_length=1, max_length=30, description="Cor do veículo")
    preco: float = Field(..., gt=0, description="Preço do veículo")
    descricao: Optional[str] = Field(None, max_length=500, description="Descrição opcional")


class VeiculoCreate(VeiculoBase):
    """Payload para criação de veículo.

    Parâmetros:
        Herda de VeiculoBase.

    Retorna:
        VeiculoCreate: Objeto pronto para persistência.
    """
    pass


class VeiculoUpdate(BaseModel):
    """Payload para atualização completa do veículo.

    Parâmetros:
        placa, marca, modelo, ano, cor, preco, descricao: Campos obrigatórios para substituir o registro.

    Retorna:
        VeiculoUpdate: Objeto validado para atualização total.
    """
    placa: str = Field(..., min_length=7, max_length=10)
    marca: str = Field(..., min_length=1, max_length=50)
    modelo: str = Field(..., min_length=1, max_length=100)
    ano: int = Field(..., ge=1900, le=2100)
    cor: str = Field(..., min_length=1, max_length=30)
    preco: float = Field(..., gt=0)
    descricao: Optional[str] = Field(None, max_length=500)


class VeiculoPatch(BaseModel):
    """Payload opcional para atualização parcial do veículo.

    Parâmetros:
        placa, marca, modelo, ano, cor, preco, descricao: Campos opcionais que serão aplicados se fornecidos.

    Retorna:
        VeiculoPatch: Objeto com campos opcionais para patch.
    """
    placa: Optional[str] = Field(None, min_length=7, max_length=10)
    marca: Optional[str] = Field(None, min_length=1, max_length=50)
    modelo: Optional[str] = Field(None, min_length=1, max_length=100)
    ano: Optional[int] = Field(None, ge=1900, le=2100)
    cor: Optional[str] = Field(None, min_length=1, max_length=30)
    preco: Optional[float] = Field(None, gt=0)
    descricao: Optional[str] = Field(None, max_length=500)


class VeiculoResponse(VeiculoBase):
    """Schema retornado pela API ao exibir veículos.

    Parâmetros:
        id (int): Identificador do veículo.
        created_at (datetime): Data de criação.
        updated_at (datetime): Última atualização.

    Retorna:
        VeiculoResponse: Objeto serializável com informações de veículo.
    """
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class VeiculoFilter(BaseModel):
    """Campos de filtro utilizados na busca de veículos.

    Parâmetros:
        marca (str | None): Marca para filtrar.
        ano (int | None): Ano para filtrar.
        cor (str | None): Cor para filtrar.
        min_preco (float | None): Preço mínimo.
        max_preco (float | None): Preço máximo.

    Retorna:
        VeiculoFilter: Objeto com filtros opcionais e aliases de query.
    """
    marca: Optional[str] = None
    ano: Optional[int] = None
    cor: Optional[str] = None
    min_preco: Optional[float] = Field(None, ge=0, alias="minPreco")
    max_preco: Optional[float] = Field(None, ge=0, alias="maxPreco")
    
    model_config = ConfigDict(populate_by_name=True)


class VeiculoMarcaReport(BaseModel):
    """Resumo agregando quantidade de veículos por marca.

    Parâmetros:
        marca (str): Nome da marca.
        quantidade (int): Total de veículos cadastrados para a marca.

    Retorna:
        VeiculoMarcaReport: Linha de relatório por marca.
    """

    marca: str
    quantidade: int
