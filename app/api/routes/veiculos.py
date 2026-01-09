from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.veiculo import (
    VeiculoCreate,
    VeiculoUpdate,
    VeiculoPatch,
    VeiculoResponse,
    VeiculoFilter,
    VeiculoMarcaReport,
)
from app.services.veiculo_service import VeiculoService
from app.api.dependencies import require_admin, get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/veiculos", tags=["Veículos"])


@router.get("", response_model=List[VeiculoResponse])
async def get_veiculos(
    marca: Optional[str] = Query(None, description="Filtrar por marca"),
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    cor: Optional[str] = Query(None, description="Filtrar por cor"),
    minPreco: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
    maxPreco: Optional[float] = Query(None, ge=0, description="Preço máximo"),
    page: int = Query(1, ge=1, description="Número da página"),
    pageSize: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    sortBy: Optional[str] = Query("created_at", description="Campo de ordenação (preco, ano, marca, created_at, updated_at)"),
    sortOrder: Optional[str] = Query("asc", description="Ordem de ordenação: asc ou desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista veículos, com filtros opcionais por marca, ano, cor ou faixa de preço.

    Parâmetros:
        marca (Optional[str]): Marca para filtrar.
        ano (Optional[int]): Ano de fabricação para filtrar.
        cor (Optional[str]): Cor para filtrar.
        minPreco (Optional[float]): Preço mínimo permitido (alias min_preco).
        maxPreco (Optional[float]): Preço máximo permitido (alias max_preco).
        db (Session): Sessão de banco de dados.
        current_user (User): Usuário autenticado e ativo exigido pelo endpoint.

    Retorna:
        List[VeiculoResponse]: Lista de veículos encontrados conforme filtros aplicados.
    """
    service = VeiculoService(db)
    
    if minPreco is not None and maxPreco is not None and minPreco > maxPreco:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="minPreco não pode ser maior que maxPreco"
        )

    if any([marca, ano, cor, minPreco is not None, maxPreco is not None, page, pageSize, sortBy, sortOrder]):
        filters = VeiculoFilter(
            marca=marca,
            ano=ano,
            cor=cor,
            minPreco=minPreco,
            maxPreco=maxPreco,
            page=page,
            pageSize=pageSize,
            sortBy=sortBy,
            sortOrder=sortOrder
        )
        return service.search_veiculos(filters)
    
    return service.get_all_veiculos()


@router.get("/{id}", response_model=VeiculoResponse)
async def get_veiculo(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Busca um veículo específico pelo ID.

    Parâmetros:
        id (int): Identificador do veículo.
        db (Session): Sessão de banco de dados.
        current_user (User): Usuário autenticado e ativo exigido pelo endpoint.

    Retorna:
        VeiculoResponse: Dados do veículo quando encontrado; 404 caso não exista.
    """
    service = VeiculoService(db)
    veiculo = service.get_veiculo_by_id(id)
    
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veículo com ID {id} não encontrado"
        )
    
    return veiculo


@router.post("", response_model=VeiculoResponse, status_code=status.HTTP_201_CREATED)
async def create_veiculo(
    veiculo_data: VeiculoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Cria um novo veículo (apenas ADMIN).

    Parâmetros:
        veiculo_data (VeiculoCreate): Dados completos do veículo a ser cadastrado.
        db (Session): Sessão de banco usada pelo repositório.
        current_user (User): Usuário autenticado com role ADMIN.

    Retorna:
        VeiculoResponse: Veículo criado com ID gerado e timestamps.
    """
    service = VeiculoService(db)
    try:
        return service.create_veiculo(veiculo_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.put("/{id}", response_model=VeiculoResponse)
async def update_veiculo(
    id: int,
    veiculo_data: VeiculoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Atualiza totalmente os dados de um veículo existente (ADMIN).

    Parâmetros:
        id (int): Identificador do veículo a ser atualizado.
        veiculo_data (VeiculoUpdate): Payload completo com os novos valores.
        db (Session): Sessão de banco.
        current_user (User): Usuário autenticado com role ADMIN.

    Retorna:
        VeiculoResponse: Veículo atualizado; 404 se o ID não existir.
    """
    service = VeiculoService(db)
    try:
        veiculo = service.update_veiculo(id, veiculo_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veículo com ID {id} não encontrado"
        )
    
    return veiculo


@router.patch("/{id}", response_model=VeiculoResponse)
async def patch_veiculo(
    id: int,
    veiculo_data: VeiculoPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Atualiza parcialmente campos de um veículo (ADMIN).

    Parâmetros:
        id (int): Identificador do veículo.
        veiculo_data (VeiculoPatch): Campos opcionais a serem alterados.
        db (Session): Sessão de banco.
        current_user (User): Usuário autenticado com role ADMIN.

    Retorna:
        VeiculoResponse: Veículo atualizado; 404 se não encontrado.
    """
    service = VeiculoService(db)
    try:
        veiculo = service.patch_veiculo(id, veiculo_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veículo com ID {id} não encontrado"
        )
    
    return veiculo


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_veiculo(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Remove logicamente um veículo pelo ID (soft delete, ADMIN).

    Parâmetros:
        id (int): Identificador do veículo a ser removido.
        db (Session): Sessão de banco.
        current_user (User): Usuário autenticado com role ADMIN.

    Retorna:
        None: Resposta 204 sem corpo quando sucesso; 404 se não encontrado.
    """
    service = VeiculoService(db)
    deleted = service.delete_veiculo(id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veículo com ID {id} não encontrado"
        )
    
    return None


@router.get("/relatorios/por-marca", response_model=List[VeiculoMarcaReport])
async def relatorio_por_marca(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retorna contagem de veículos agrupada por marca.

    Parâmetros:
        db (Session): Sessão de banco.
        current_user (User): Usuário autenticado e ativo.

    Retorna:
        List[VeiculoMarcaReport]: Lista com marca e quantidade.
    """
    service = VeiculoService(db)
    return service.report_por_marca()
