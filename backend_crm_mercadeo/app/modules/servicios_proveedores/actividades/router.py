from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_username
from app.modules.servicios_proveedores.actividades.dependencies import get_actividad_service
from app.modules.servicios_proveedores.actividades.schemas import (
    ActividadCreate,
    ActividadListado,
    ActividadRead,
    ActividadUpdate,
)
from app.modules.servicios_proveedores.actividades.service import ActividadService

router = APIRouter(
    prefix="/actividades", tags=["Actividades"], dependencies=[Depends(get_current_username)]
)


@router.get("/", response_model=ActividadListado)
def list_actividades(
    q: str | None = Query(None, description="Busca por nombre o descripcion"),
    proveedor_id: int | None = None,
    skip: int = 0,
    limit: int = Query(100, ge=1, le=200),
    service: ActividadService = Depends(get_actividad_service),
) -> ActividadListado:
    return service.list(q=q, proveedor_id=proveedor_id, skip=skip, limit=limit)


@router.get("/{actividad_id}", response_model=ActividadRead)
def get_actividad(
    actividad_id: int, service: ActividadService = Depends(get_actividad_service)
) -> ActividadRead:
    return service.get(actividad_id)


@router.post("/", response_model=ActividadRead, status_code=status.HTTP_201_CREATED)
def create_actividad(
    data: ActividadCreate, service: ActividadService = Depends(get_actividad_service)
) -> ActividadRead:
    return service.create(data)


@router.put("/{actividad_id}", response_model=ActividadRead)
def update_actividad(
    actividad_id: int,
    data: ActividadUpdate,
    service: ActividadService = Depends(get_actividad_service),
) -> ActividadRead:
    return service.update(actividad_id, data)


@router.delete("/{actividad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_actividad(
    actividad_id: int, service: ActividadService = Depends(get_actividad_service)
) -> None:
    service.delete(actividad_id)
