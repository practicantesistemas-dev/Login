from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_username
from app.modules.administracion.bitacora.dependencies import get_bitacora_service
from app.modules.administracion.bitacora.schemas import (
    BitacoraCreate,
    BitacoraListado,
    BitacoraRead,
)
from app.modules.administracion.bitacora.service import BitacoraService
from app.shared.enums import TipoActividadBitacora

router = APIRouter(
    prefix="/bitacora", tags=["Bitacora"], dependencies=[Depends(get_current_username)]
)


@router.get("/", response_model=BitacoraListado)
def listar_bitacora(
    tipo: TipoActividadBitacora | None = None,
    q: str | None = Query(None, description="Busca por contacto, empresa o accion"),
    contacto_id: int | None = None,
    oportunidad_id: int | None = None,
    titular_id: int | None = None,
    skip: int = 0,
    limit: int = Query(100, ge=1, le=200),
    service: BitacoraService = Depends(get_bitacora_service),
) -> BitacoraListado:
    return service.listar(
        tipo=tipo,
        q=q,
        contacto_id=contacto_id,
        oportunidad_id=oportunidad_id,
        titular_id=titular_id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=BitacoraRead, status_code=status.HTTP_201_CREATED)
def registrar_seguimiento(
    data: BitacoraCreate,
    username: str = Depends(get_current_username),
    service: BitacoraService = Depends(get_bitacora_service),
) -> BitacoraRead:
    return service.create(data, username=username)


@router.delete("/{id_bitacora}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_seguimiento(
    id_bitacora: int,
    username: str = Depends(get_current_username),
    service: BitacoraService = Depends(get_bitacora_service),
) -> None:
    service.delete(id_bitacora)
