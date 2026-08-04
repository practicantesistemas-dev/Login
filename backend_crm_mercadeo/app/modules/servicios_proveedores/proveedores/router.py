from fastapi import APIRouter, Depends, Query, status

from app.modules.servicios_proveedores.actividades.dependencies import get_actividad_service
from app.modules.servicios_proveedores.actividades.schemas import ActividadListado
from app.modules.servicios_proveedores.actividades.service import ActividadService
from app.modules.servicios_proveedores.proveedores.dependencies import get_proveedor_service
from app.modules.servicios_proveedores.proveedores.schemas import (
    ProveedorCreate,
    ProveedorListado,
    ProveedorRead,
    ProveedorUpdate,
)
from app.modules.servicios_proveedores.proveedores.service import ProveedorService

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@router.get("/", response_model=ProveedorListado)
def list_proveedores(
    q: str | None = Query(None, description="Busca por nombre, NIT, correo o categoria"),
    estado: bool | None = None,
    categoria: str | None = None,
    skip: int = 0,
    limit: int = Query(100, ge=1, le=200),
    service: ProveedorService = Depends(get_proveedor_service),
) -> ProveedorListado:
    return service.list(q=q, estado=estado, categoria=categoria, skip=skip, limit=limit)


@router.get("/categorias", response_model=list[str])
def list_categorias_proveedores(
    service: ProveedorService = Depends(get_proveedor_service),
) -> list[str]:
    return service.categorias()


@router.get("/{proveedor_id}", response_model=ProveedorRead)
def get_proveedor(
    proveedor_id: int, service: ProveedorService = Depends(get_proveedor_service)
) -> ProveedorRead:
    return service.get(proveedor_id)


@router.get("/{proveedor_id}/actividades", response_model=ActividadListado)
def list_actividades_proveedor(
    proveedor_id: int,
    skip: int = 0,
    limit: int = Query(100, ge=1, le=200),
    proveedor_service: ProveedorService = Depends(get_proveedor_service),
    actividad_service: ActividadService = Depends(get_actividad_service),
) -> ActividadListado:
    proveedor_service.get(proveedor_id)
    return actividad_service.list(proveedor_id=proveedor_id, skip=skip, limit=limit)


@router.post("/", response_model=ProveedorRead, status_code=status.HTTP_201_CREATED)
def create_proveedor(
    data: ProveedorCreate, service: ProveedorService = Depends(get_proveedor_service)
) -> ProveedorRead:
    return service.create(data)


@router.put("/{proveedor_id}", response_model=ProveedorRead)
def update_proveedor(
    proveedor_id: int,
    data: ProveedorUpdate,
    service: ProveedorService = Depends(get_proveedor_service),
) -> ProveedorRead:
    return service.update(proveedor_id, data)


@router.delete("/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proveedor(
    proveedor_id: int, service: ProveedorService = Depends(get_proveedor_service)
) -> None:
    service.delete(proveedor_id)
