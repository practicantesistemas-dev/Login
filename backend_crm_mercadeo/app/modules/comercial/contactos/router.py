from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_username
from app.modules.administracion.bitacora.dependencies import get_bitacora_service
from app.modules.administracion.bitacora.schemas import BitacoraItem
from app.modules.administracion.bitacora.service import BitacoraService
from app.modules.comercial.contactos.dependencies import get_contacto_service
from app.modules.comercial.contactos.schemas import ContactoCreate, ContactoRead, ContactoUpdate
from app.modules.comercial.contactos.service import ContactoService
from app.shared.enums import TipoContacto

router = APIRouter(
    prefix="/contactos", tags=["Contactos"], dependencies=[Depends(get_current_username)]
)


@router.get("/", response_model=list[ContactoRead])
def list_contactos(
    q: str | None = Query(None, description="Busca por nombre, cedula o empresa"),
    estado: str | None = None,
    municipio: str | None = None,
    departamento: str | None = None,
    responsable_id: int | None = None,
    sexo: str | None = None,
    tipo_contacto: TipoContacto | None = None,
    edad_min: int | None = Query(None, ge=0),
    edad_max: int | None = Query(None, ge=0),
    skip: int = 0,
    limit: int = Query(6, ge=1, le=6),
    service: ContactoService = Depends(get_contacto_service),
) -> list[ContactoRead]:
    return service.list(
        q=q,
        estado=estado,
        municipio=municipio,
        departamento=departamento,
        responsable_id=responsable_id,
        sexo=sexo,
        tipo_contacto=tipo_contacto,
        edad_min=edad_min,
        edad_max=edad_max,
        skip=skip,
        limit=limit,
    )


@router.get("/{contacto_id}", response_model=ContactoRead)
def get_contacto(
    contacto_id: int, service: ContactoService = Depends(get_contacto_service)
) -> ContactoRead:
    return service.get(contacto_id)


@router.post("/", response_model=ContactoRead, status_code=status.HTTP_201_CREATED)
def create_contacto(
    data: ContactoCreate,
    username: str = Depends(get_current_username),
    service: ContactoService = Depends(get_contacto_service),
) -> ContactoRead:
    return service.create(data, username=username)


@router.get("/{contacto_id}/bitacora", response_model=list[BitacoraItem])
def historial_bitacora_contacto(
    contacto_id: int,
    limit: int = Query(4, ge=1, le=50),
    contacto_service: ContactoService = Depends(get_contacto_service),
    bitacora_service: BitacoraService = Depends(get_bitacora_service),
) -> list[BitacoraItem]:
    contacto_service.get(contacto_id)
    return bitacora_service.historial_contacto(contacto_id, limit=limit)


@router.put("/{contacto_id}", response_model=ContactoRead)
def update_contacto(
    contacto_id: int,
    data: ContactoUpdate,
    username: str = Depends(get_current_username),
    service: ContactoService = Depends(get_contacto_service),
) -> ContactoRead:
    return service.update(contacto_id, data, username=username)


@router.delete("/{contacto_id}/etiquetas/{etiqueta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_etiqueta_contacto(
    contacto_id: int,
    etiqueta_id: int,
    service: ContactoService = Depends(get_contacto_service),
) -> None:
    service.eliminar_etiqueta(contacto_id, etiqueta_id)


@router.delete("/{contacto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contacto(
    contacto_id: int, service: ContactoService = Depends(get_contacto_service)
) -> None:
    service.delete(contacto_id)
