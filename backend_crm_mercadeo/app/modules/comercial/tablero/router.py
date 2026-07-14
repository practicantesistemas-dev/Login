from fastapi import APIRouter, Depends, Query

from app.modules.comercial.tablero.dependencies import get_tablero_service
from app.modules.comercial.tablero.schemas import (
    ActividadRecienteItem,
    DistribucionContactos,
    Periodo,
    ResumenDashboard,
    TopServicioItem,
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


@router.get("/top-servicios", response_model=list[TopServicioItem])
def get_top_servicios(
    limit: int = Query(4, ge=1, le=20),
    service: TableroService = Depends(get_tablero_service),
) -> list[TopServicioItem]:
    return service.top_servicios(limit=limit)
