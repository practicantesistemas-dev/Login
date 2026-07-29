from fastapi import APIRouter, Depends, Query

from app.modules.compartidos.ubicaciones.dependencies import get_ubicaciones_service
from app.modules.compartidos.ubicaciones.schemas import DepartamentoItem, MunicipioItem
from app.modules.compartidos.ubicaciones.service import UbicacionesService

router = APIRouter(prefix="/compartidos/ubicaciones", tags=["Compartidos"])


@router.get("/departamentos", response_model=list[DepartamentoItem])
def get_departamentos(
    q: str | None = Query(None, description="Busca departamentos por nombre"),
    service: UbicacionesService = Depends(get_ubicaciones_service),
) -> list[DepartamentoItem]:
    return service.listar_departamentos(q)


@router.get("/municipios", response_model=list[MunicipioItem])
def get_municipios(
    departamento: str | None = Query(
        None, description="Codigo o nombre (parcial) del departamento para filtrar"
    ),
    q: str | None = Query(None, description="Busca municipios por nombre"),
    service: UbicacionesService = Depends(get_ubicaciones_service),
) -> list[MunicipioItem]:
    return service.listar_municipios(departamento, q)
