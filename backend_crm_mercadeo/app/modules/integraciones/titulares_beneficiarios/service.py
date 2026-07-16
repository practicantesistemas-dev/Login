from sqlalchemy.orm import Session

from app.modules.integraciones.titulares_beneficiarios.repository import (
    TitularesBeneficiariosRepository,
)
from app.modules.integraciones.titulares_beneficiarios.schemas import (
    ListadoTitulares,
    PlanItem,
    ResumenTitularesBeneficiarios,
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

    def listar_titulares(
        self,
        limit: int = 6,
        estado: str | None = None,
        plan: str | None = None,
        sexo: str | None = None,
        edad: str | None = None,
    ) -> list[ListadoTitulares]:
        filas = self.repository.listar_titulares(limit, estado, plan, sexo, edad)
        return [ListadoTitulares(**fila) for fila in filas]

    def listar_planes(self) -> list[PlanItem]:
        return [
            PlanItem(
                ID=servicio.id,
                NOMBRE=servicio.nombre,
                CATEGORIA=servicio.categoria,
                TIPO=servicio.tipo,
                MAX_BENEFICIARIOS=servicio.max_beneficiarios,
                DESCRIPCION=servicio.descripcion,
                ESTADO=servicio.estado,
            )
            for servicio in self.repository.listar_planes()
        ]

    def listar_nombres_planes(self) -> list[str]:
        return self.repository.listar_nombres_planes()
