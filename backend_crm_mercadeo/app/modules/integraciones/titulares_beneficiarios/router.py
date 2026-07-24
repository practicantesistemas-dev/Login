from fastapi import APIRouter, Depends, status

from app.modules.integraciones.titulares_beneficiarios.dependencies import (
    get_titulares_beneficiarios_service,
)
from app.modules.integraciones.titulares_beneficiarios.schemas import (
    ActivacionBeneficiarioResultado,
    ActivacionTitularResultado,
    BeneficiarioActivar,
    BeneficiarioCrear,
    BeneficiarioDetalle,
    BeneficiarioUpdate,
    CreacionBeneficiarioResultado,
    CreacionTitularResultado,
    DesactivacionBeneficiarioResultado,
    DesactivacionTitularResultado,
    ListadoTitularesPaginado,
    PlanItem,
    PlanNombre,
    ResumenTitularesBeneficiarios,
    TitularActivar,
    TitularCrear,
    TitularDetalle,
    TitularUpdate,
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


@router.get("/listado", response_model=ListadoTitularesPaginado)
def get_listado(
    limit: int = 6,
    offset: int = 0,
    estado: str | None = None,
    tipo_plan_id: int | None = None,
    sexo: str | None = None,
    edad: str | None = None,
    busqueda: str | None = None,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> ListadoTitularesPaginado:
    return service.listar_titulares(limit, offset, estado, tipo_plan_id, sexo, edad, busqueda)


@router.get("/planes", response_model=list[PlanItem])
def get_planes(
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> list[PlanItem]:
    return service.listar_planes()


@router.get("/planes/nombres", response_model=list[PlanNombre])
def get_nombres_planes(
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> list[PlanNombre]:
    return service.listar_nombres_planes()


@router.get("/{id_titular}/beneficiarios", response_model=list[BeneficiarioDetalle])
def get_beneficiarios(
    id_titular: int,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> list[BeneficiarioDetalle]:
    return service.listar_beneficiarios(id_titular)


@router.post(
    "/{id_titular}/beneficiarios",
    response_model=CreacionBeneficiarioResultado,
    status_code=status.HTTP_201_CREATED,
)
def crear_beneficiario(
    id_titular: int,
    data: BeneficiarioCrear,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> CreacionBeneficiarioResultado:
    return service.crear_beneficiario(id_titular, data)


@router.patch("/{id_titular}/beneficiarios/{id_beneficiario}", response_model=BeneficiarioDetalle)
def update_beneficiario(
    id_titular: int,
    id_beneficiario: int,
    data: BeneficiarioUpdate,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> BeneficiarioDetalle:
    return service.actualizar_beneficiario(id_titular, id_beneficiario, data)


@router.post(
    "/{id_titular}/beneficiarios/{id_beneficiario}/activar",
    response_model=ActivacionBeneficiarioResultado,
)
def activar_beneficiario(
    id_titular: int,
    id_beneficiario: int,
    data: BeneficiarioActivar,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> ActivacionBeneficiarioResultado:
    return service.activar_beneficiario(id_titular, id_beneficiario, data.FECHA_INGRESO)


@router.post(
    "/{id_titular}/beneficiarios/{id_beneficiario}/desactivar",
    response_model=DesactivacionBeneficiarioResultado,
)
def desactivar_beneficiario(
    id_titular: int,
    id_beneficiario: int,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> DesactivacionBeneficiarioResultado:
    return service.desactivar_beneficiario(id_titular, id_beneficiario)


@router.post(
    "",
    response_model=CreacionTitularResultado,
    status_code=status.HTTP_201_CREATED,
)
def crear_titular(
    data: TitularCrear,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> CreacionTitularResultado:
    return service.crear_titular(data)


@router.get("/{id_titular}", response_model=TitularDetalle)
def get_titular(
    id_titular: int,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> TitularDetalle:
    return service.obtener_titular(id_titular)


@router.patch("/{id_titular}", response_model=TitularDetalle)
def update_titular(
    id_titular: int,
    data: TitularUpdate,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> TitularDetalle:
    return service.actualizar_titular(id_titular, data)


@router.post("/{id_titular}/activar", response_model=ActivacionTitularResultado)
def activar_titular(
    id_titular: int,
    data: TitularActivar,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> ActivacionTitularResultado:
    return service.activar_titular(id_titular, data.FECHA_INGRESO)


@router.post("/{id_titular}/desactivar", response_model=DesactivacionTitularResultado)
def desactivar_titular(
    id_titular: int,
    service: TitularesBeneficiariosService = Depends(get_titulares_beneficiarios_service),
) -> DesactivacionTitularResultado:
    return service.desactivar_titular(id_titular)
