from fastapi import APIRouter, Depends

from app.modules.integraciones.titulares_beneficiarios.dependencies import (
    get_titulares_beneficiarios_service,
)
from app.modules.integraciones.titulares_beneficiarios.schemas import (
    ListadoTitulares,
    PlanItem,
    ResumenTitularesBeneficiarios,
    TitularDetalle,
)
from app.modules.integraciones.titulares_beneficiarios.service import (
    TitularesBeneficiariosService,
)

router = APIRouter(prefix="/titulares-beneficiarios", tags=["Titulares y Beneficiarios"])


@router.get("/resumen", response_model=ResumenTitularesBeneficiarios)
def get_resumen(
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> ResumenTitularesBeneficiarios:
    return service.resumen()


@router.get("/listado", response_model=list[ListadoTitulares])
def get_listado(
    limit: int = 6,
    estado: str | None = None,
    plan: str | None = None,
    sexo: str | None = None,
    edad: str | None = None,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> list[ListadoTitulares]:
    return service.listar_titulares(limit, estado, plan, sexo, edad)


@router.get("/planes", response_model=list[PlanItem])
def get_planes(
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> list[PlanItem]:
    return service.listar_planes()


@router.get("/planes/nombres", response_model=list[str])
def get_nombres_planes(
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> list[str]:
    return service.listar_nombres_planes()


@router.get("/{id_titular}", response_model=TitularDetalle)
def get_titular(
    id_titular: int,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> TitularDetalle:
    return service.obtener_titular(id_titular)
