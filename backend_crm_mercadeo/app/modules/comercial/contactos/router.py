from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_username
from app.modules.comercial.contactos.dependencies import get_contacto_service
from app.modules.comercial.contactos.schemas import ContactoCreate, ContactoRead
from app.modules.comercial.contactos.service import ContactoService

router = APIRouter(prefix="/contactos", tags=["Contactos"])


@router.get("/", response_model=list[ContactoRead])
def list_contactos(
    skip: int = 0,
    limit: int = 100,
    service: ContactoService = Depends(get_contacto_service),
) -> list[ContactoRead]:
    return service.list(skip=skip, limit=limit)


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
