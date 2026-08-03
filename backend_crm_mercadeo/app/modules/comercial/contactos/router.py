from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_username
from app.modules.comercial.contactos.dependencies import get_contacto_service
from app.modules.comercial.contactos.schemas import ContactoCreate, ContactoRead
from app.modules.comercial.contactos.service import ContactoService
from app.shared.enums import TipoContacto

router = APIRouter(prefix="/contactos", tags=["Contactos"])


@router.get("/", response_model=list[ContactoRead])
def list_contactos(
    q: str | None = Query(None, description="Busca por nombre, cedula o empresa"),
    estado: str | None = None,
    ciudad: str | None = None,
    responsable_id: int | None = None,
    sexo: str | None = None,
    tipo_contacto: TipoContacto | None = None,
    edad_min: int | None = Query(None, ge=0),
    edad_max: int | None = Query(None, ge=0),
    skip: int = 0,
    limit: int = 100,
    service: ContactoService = Depends(get_contacto_service),
) -> list[ContactoRead]:
    return service.list(
        q=q,
        estado=estado,
        ciudad=ciudad,
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


@router.delete("/{contacto_id}/etiquetas/{etiqueta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_etiqueta_contacto(
    contacto_id: int,
    etiqueta_id: int,
    service: ContactoService = Depends(get_contacto_service),
) -> None:
    service.eliminar_etiqueta(contacto_id, etiqueta_id)
