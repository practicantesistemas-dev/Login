from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_username
from app.modules.comercial.oportunidades.dependencies import get_oportunidad_service
from app.modules.comercial.oportunidades.schemas import (
    OportunidadCreate,
    OportunidadRead,
    OportunidadUpdate,
)
from app.modules.comercial.oportunidades.service import OportunidadService

router = APIRouter(
    prefix="/oportunidades", tags=["Oportunidades"], dependencies=[Depends(get_current_username)]
)


@router.get("/", response_model=list[OportunidadRead])
def list_oportunidades(
    skip: int = 0,
    limit: int = 200,
    service: OportunidadService = Depends(get_oportunidad_service),
) -> list[OportunidadRead]:
    return service.listar(skip=skip, limit=limit)


@router.get("/{oportunidad_id}", response_model=OportunidadRead)
def get_oportunidad(
    oportunidad_id: int, service: OportunidadService = Depends(get_oportunidad_service)
) -> OportunidadRead:
    return service.obtener(oportunidad_id)


@router.post("/", response_model=OportunidadRead, status_code=status.HTTP_201_CREATED)
def create_oportunidad(
    data: OportunidadCreate,
    username: str = Depends(get_current_username),
    service: OportunidadService = Depends(get_oportunidad_service),
) -> OportunidadRead:
    return service.crear(data, username=username)


@router.patch("/{oportunidad_id}", response_model=OportunidadRead)
def update_oportunidad(
    oportunidad_id: int,
    data: OportunidadUpdate,
    service: OportunidadService = Depends(get_oportunidad_service),
) -> OportunidadRead:
    return service.actualizar(oportunidad_id, data)


@router.delete("/{oportunidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_oportunidad(
    oportunidad_id: int, service: OportunidadService = Depends(get_oportunidad_service)
) -> None:
    service.eliminar(oportunidad_id)
