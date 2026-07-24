from fastapi import APIRouter, Depends, Query

from app.modules.comercial.tablero.dependencies import get_tablero_service
from app.modules.comercial.tablero.schemas import (
    ActividadRecienteItem,
    DistribucionContactos,
    EtapaEmbudoItem,
    Periodo,
    ResumenDashboard,
    TopPlanItem,
)
from app.modules.comercial.tablero.service import TableroService

router = APIRouter(prefix="/tablero", tags=["Tablero"])


@router.get("/resumen", response_model=ResumenDashboard)
def get_resumen(
    periodo: Periodo = Query(
        "30d", description="7d, 30d, trimestre, anio o todo (sin filtro de fecha)"
    ),
    service: TableroService = Depends(get_tablero_service),
) -> ResumenDashboard:
    return service.resumen(periodo=periodo)


@router.get("/actividad-reciente", response_model=list[ActividadRecienteItem])
def get_actividad_reciente(
    limit: int = Query(10, ge=1, le=50),
    service: TableroService = Depends(get_tablero_service),
) -> list[ActividadRecienteItem]:
    return service.actividad_reciente(limit=limit)


@router.get("/distribucion-contactos", response_model=DistribucionContactos)
def get_distribucion_contactos(
    periodo: Periodo = Query(
        "30d", description="7d, 30d, trimestre, anio o todo (sin filtro de fecha)"
    ),
    service: TableroService = Depends(get_tablero_service),
) -> DistribucionContactos:
    return service.distribucion_contactos(periodo=periodo)


@router.get("/embudo-comercial", response_model=list[EtapaEmbudoItem])
def get_embudo_comercial(
    embudo_id: int | None = Query(
        None, description="Filtra por un embudo especifico; si se omite, trae todas las etapas"
    ),
    periodo: Periodo = Query(
        "30d", description="7d, 30d, trimestre, anio o todo (sin filtro de fecha)"
    ),
    service: TableroService = Depends(get_tablero_service),
) -> list[EtapaEmbudoItem]:
    return service.embudo_comercial(embudo_id=embudo_id, periodo=periodo)


@router.get("/top-planes", response_model=list[TopPlanItem])
def get_top_planes(
    limit: int = Query(4, ge=1, le=20),
    service: TableroService = Depends(get_tablero_service),
) -> list[TopPlanItem]:
    return service.top_planes(limit=limit)
