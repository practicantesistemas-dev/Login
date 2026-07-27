from fastapi import APIRouter, Depends, status

from app.modules.administracion.bitacora.dependencies import get_bitacora_service
from app.modules.administracion.bitacora.schemas import BitacoraCreate, BitacoraRead
from app.modules.administracion.bitacora.service import BitacoraService

router = APIRouter(prefix="/bitacora", tags=["Bitacora"])


@router.post("/", response_model=BitacoraRead, status_code=status.HTTP_201_CREATED)
def registrar_seguimiento(
    data: BitacoraCreate, service: BitacoraService = Depends(get_bitacora_service)
) -> BitacoraRead:
    return service.create(data)
