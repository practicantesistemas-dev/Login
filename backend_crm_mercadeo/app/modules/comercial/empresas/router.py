from fastapi import APIRouter, Depends, status

from app.modules.comercial.empresas.dependencies import get_empresa_service
from app.modules.comercial.empresas.schemas import EmpresaCreate, EmpresaRead, EmpresaUpdate
from app.modules.comercial.empresas.service import EmpresaService

router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.get("/", response_model=list[EmpresaRead])
def list_empresas(
    skip: int = 0,
    limit: int = 100,
    service: EmpresaService = Depends(get_empresa_service),
) -> list[EmpresaRead]:
    return service.list(skip=skip, limit=limit)


@router.get("/{empresa_id}", response_model=EmpresaRead)
def get_empresa(
    empresa_id: int, service: EmpresaService = Depends(get_empresa_service)
) -> EmpresaRead:
    return service.get(empresa_id)


@router.post("/", response_model=EmpresaRead, status_code=status.HTTP_201_CREATED)
def create_empresa(
    data: EmpresaCreate, service: EmpresaService = Depends(get_empresa_service)
) -> EmpresaRead:
    return service.create(data)


@router.put("/{empresa_id}", response_model=EmpresaRead)
def update_empresa(
    empresa_id: int,
    data: EmpresaUpdate,
    service: EmpresaService = Depends(get_empresa_service),
) -> EmpresaRead:
    return service.update(empresa_id, data)


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_empresa(
    empresa_id: int, service: EmpresaService = Depends(get_empresa_service)
) -> None:
    service.delete(empresa_id)
