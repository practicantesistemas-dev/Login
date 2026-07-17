from sqlalchemy.orm import Session

from app.modules.integraciones.titulares_beneficiarios.exceptions import (
    TitularNotFoundError,
)
from app.modules.integraciones.titulares_beneficiarios.repository import (
    TitularesBeneficiariosRepository,
)
from app.modules.integraciones.titulares_beneficiarios.schemas import (
    ListadoTitulares,
    ListadoTitularesPaginado,
    PlanItem,
    ResumenTitularesBeneficiarios,
    TitularDetalle,
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

    def listar_titulares(
        self,
        limit: int = 6,
        offset: int = 0,
        estado: str | None = None,
        plan: str | None = None,
        sexo: str | None = None,
        edad: str | None = None,
    ) -> ListadoTitularesPaginado:
        filas = self.repository.listar_titulares(limit, offset, estado, plan, sexo, edad)
        total = self.repository.contar_titulares(estado, plan, sexo, edad)
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
