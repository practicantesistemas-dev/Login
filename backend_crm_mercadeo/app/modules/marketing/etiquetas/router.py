from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_username
from app.modules.marketing.etiquetas.dependencies import get_etiqueta_service
from app.modules.marketing.etiquetas.schemas import EtiquetaCreate, EtiquetaRead
from app.modules.marketing.etiquetas.service import EtiquetaService

router = APIRouter(
    prefix="/etiquetas", tags=["Etiquetas"], dependencies=[Depends(get_current_username)]
)


@router.get("/", response_model=list[EtiquetaRead])
def list_etiquetas(
    skip: int = 0,
    limit: int = 100,
    service: EtiquetaService = Depends(get_etiqueta_service),
) -> list[EtiquetaRead]:
    return service.list(skip=skip, limit=limit)


@router.post("/", response_model=EtiquetaRead, status_code=status.HTTP_201_CREATED)
def create_etiqueta(
    data: EtiquetaCreate, service: EtiquetaService = Depends(get_etiqueta_service)
) -> EtiquetaRead:
    return service.create(data)
