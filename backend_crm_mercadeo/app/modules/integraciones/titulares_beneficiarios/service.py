from sqlalchemy.orm import Session

from app.modules.integraciones.titulares_beneficiarios.exceptions import (
    BeneficiarioNotFoundError,
    TitularNotFoundError,
)
from app.modules.integraciones.titulares_beneficiarios.repository import (
    TitularesBeneficiariosRepository,
)
from app.modules.integraciones.titulares_beneficiarios.schemas import (
    BeneficiarioDetalle,
    BeneficiarioUpdate,
    ListadoTitulares,
    ListadoTitularesPaginado,
    PlanItem,
    ResumenTitularesBeneficiarios,
    TitularDetalle,
    TitularUpdate,
)


class TitularesBeneficiariosService:
    def __init__(self, db: Session) -> None:
        self.repository = TitularesBeneficiariosRepository(db)

    def resumen(self) -> ResumenTitularesBeneficiarios:
        r = self.repository
        return ResumenTitularesBeneficiarios(
            titulares_activos=r.contar_titulares_activos(),
            beneficiarios_activos=r.contar_beneficiarios_activos(),
        )

    def obtener_titular(self, id_titular: int) -> TitularDetalle:
        fila = self.repository.obtener_titular(id_titular)
        if fila is None:
            raise TitularNotFoundError(id_titular)
        return TitularDetalle(**fila)

    def listar_beneficiarios(self, id_titular: int) -> list[BeneficiarioDetalle]:
        if self.repository.obtener_titular(id_titular) is None:
            raise TitularNotFoundError(id_titular)
        filas = self.repository.listar_beneficiarios(id_titular)
        return [BeneficiarioDetalle(**fila) for fila in filas]

    def actualizar_titular(self, id_titular: int, data: TitularUpdate) -> TitularDetalle:
        cambios = data.model_dump(exclude_unset=True)
        if not self.repository.actualizar_titular(id_titular, cambios):
            raise TitularNotFoundError(id_titular)
        fila = self.repository.obtener_titular(id_titular)
        return TitularDetalle(**fila)

    def actualizar_beneficiario(
        self, id_titular: int, id_beneficiario: int, data: BeneficiarioUpdate
    ) -> BeneficiarioDetalle:
        if self.repository.obtener_titular(id_titular) is None:
            raise TitularNotFoundError(id_titular)
        cambios = data.model_dump(exclude_unset=True)
        if not self.repository.actualizar_beneficiario(id_titular, id_beneficiario, cambios):
            raise BeneficiarioNotFoundError(id_beneficiario)
        fila = self.repository.obtener_beneficiario(id_titular, id_beneficiario)
        return BeneficiarioDetalle(**fila)

    def listar_titulares(
        self,
        limit: int = 6,
        offset: int = 0,
        estado: str | None = None,
        plan: str | None = None,
        sexo: str | None = None,
        edad: str | None = None,
        busqueda: str | None = None,
    ) -> ListadoTitularesPaginado:
        filas = self.repository.listar_titulares(
            limit, offset, estado, plan, sexo, edad, busqueda
        )
        total = self.repository.contar_titulares(estado, plan, sexo, edad, busqueda)
        return ListadoTitularesPaginado(
            items=[ListadoTitulares(**fila) for fila in filas],
            total=total,
            limit=limit,
            offset=offset,
        )

    def listar_planes(self) -> list[PlanItem]:
        return [
            PlanItem(
                ID=servicio.id,
                NOMBRE=(
                    f"{servicio.nombre} - {servicio.categoria}"
                    if servicio.categoria
                    else servicio.nombre
                ),
                TIPO=servicio.tipo,
                MAX_BENEFICIARIOS=servicio.max_beneficiarios,
                BENEFICIARIOS_ADICIONALES=servicio.beneficiarios_adicionales,
                DESCRIPCION=servicio.descripcion,
                ESTADO=servicio.estado,
            )
            for servicio in self.repository.listar_planes()
        ]

    def listar_nombres_planes(self) -> list[str]:
        return self.repository.listar_nombres_planes()
