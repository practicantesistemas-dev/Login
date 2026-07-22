from datetime import date

from sqlalchemy.orm import Session

from app.modules.integraciones.titulares_beneficiarios.exceptions import (
    BeneficiarioNotFoundError,
    DocumentoDuplicadoError,
    TitularInactivoError,
    TitularNotFoundError,
)
from app.modules.integraciones.titulares_beneficiarios.legacy_repository import (
    LegacyRepository,
)
from app.modules.integraciones.titulares_beneficiarios.repository import (
    ESTADO_ACTIVO,
    TitularesBeneficiariosRepository,
)
from app.modules.integraciones.titulares_beneficiarios.schemas import (
    ActivacionBeneficiarioResultado,
    ActivacionTitularResultado,
    BeneficiarioDetalle,
    BeneficiarioUpdate,
    CreacionTitularResultado,
    DesactivacionBeneficiarioResultado,
    DesactivacionTitularResultado,
    ListadoTitulares,
    ListadoTitularesPaginado,
    PlanItem,
    PlanNombre,
    ResumenTitularesBeneficiarios,
    TitularCrear,
    TitularDetalle,
    TitularUpdate,
)


class TitularesBeneficiariosService:
    def __init__(self, db: Session) -> None:
        self.repository = TitularesBeneficiariosRepository(db)
        self.legacy_repository = LegacyRepository(db)

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

    def crear_titular(self, data: TitularCrear) -> CreacionTitularResultado:
        duplicado = self.repository.existe_documento(data.TIPO_DOCUMENTO, data.DOCUMENTO)
        if duplicado is not None:
            raise DocumentoDuplicadoError(data.DOCUMENTO, duplicado)

        datos = data.model_dump(exclude={"FECHA_INGRESO", "SERVICIO_ID"})
        self.legacy_repository.crear_preplanliga(datos)

        id_titular = self.repository.crear_titular(datos, data.FECHA_INGRESO)
        self.repository.asociar_servicio(id_titular, data.SERVICIO_ID)

        usuario_creado = self.legacy_repository.crear_usuario_servinte(
            data.TIPO_DOCUMENTO, data.DOCUMENTO, data.NOMBRE1, data.NOMBRE2,
            data.APELLIDO1, data.APELLIDO2,
        )
        nombre_completo = " ".join(
            parte for parte in [data.NOMBRE1, data.NOMBRE2, data.APELLIDO1, data.APELLIDO2]
            if parte
        )
        marcado_incle = self.legacy_repository.marcar_nuevo_titular_incle(
            data.TIPO_DOCUMENTO, data.DOCUMENTO, nombre_completo
        )

        fila = self.repository.obtener_titular(id_titular)
        return CreacionTitularResultado(
            titular=TitularDetalle(**fila),
            usuario_servinte_creado=usuario_creado,
            marcado_en_incle=marcado_incle,
        )

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

    def activar_beneficiario(
        self, id_titular: int, id_beneficiario: int, fecha_ingreso: date
    ) -> ActivacionBeneficiarioResultado:
        titular = self.repository.obtener_titular(id_titular)
        if titular is None:
            raise TitularNotFoundError(id_titular)
        if titular["ESTADO"] != ESTADO_ACTIVO:
            raise TitularInactivoError(id_titular)

        if not self.repository.activar_beneficiario(id_titular, id_beneficiario, fecha_ingreso):
            raise BeneficiarioNotFoundError(id_beneficiario)
        fila = self.repository.obtener_beneficiario(id_titular, id_beneficiario)
        num_incle = self.legacy_repository.desmarcar_registros_incle(
            fila["TIPO_DOCUMENTO"], fila["DOCUMENTO"]
        )
        return ActivacionBeneficiarioResultado(
            beneficiario=BeneficiarioDetalle(**fila),
            registros_incle_desmarcados=num_incle,
        )

    def desactivar_beneficiario(
        self, id_titular: int, id_beneficiario: int
    ) -> DesactivacionBeneficiarioResultado:
        if not self.repository.desactivar_beneficiario(id_titular, id_beneficiario):
            raise BeneficiarioNotFoundError(id_beneficiario)
        fila = self.repository.obtener_beneficiario(id_titular, id_beneficiario)
        num_incle = self.legacy_repository.marcar_registros_incle(
            fila["TIPO_DOCUMENTO"], fila["DOCUMENTO"]
        )
        return DesactivacionBeneficiarioResultado(
            beneficiario=BeneficiarioDetalle(**fila),
            registros_incle_marcados=num_incle,
        )

    def activar_titular(
        self, id_titular: int, fecha_ingreso: date
    ) -> ActivacionTitularResultado:
        if not self.repository.activar_titular(id_titular, fecha_ingreso):
            raise TitularNotFoundError(id_titular)
        num_beneficiarios = self.repository.activar_beneficiarios(id_titular, fecha_ingreso)
        fila = self.repository.obtener_titular(id_titular)
        num_incle = self.legacy_repository.desmarcar_registros_incle(
            fila["TIPO_DOCUMENTO"], fila["DOCUMENTO"]
        )
        return ActivacionTitularResultado(
            titular=TitularDetalle(**fila),
            beneficiarios_activados=num_beneficiarios,
            registros_incle_desmarcados=num_incle,
        )

    def desactivar_titular(self, id_titular: int) -> DesactivacionTitularResultado:
        if not self.repository.desactivar_titular(id_titular):
            raise TitularNotFoundError(id_titular)
        fila = self.repository.obtener_titular(id_titular)
        tipo, documento = fila["TIPO_DOCUMENTO"], fila["DOCUMENTO"]

        beneficiarios_desactivados = self.repository.desactivar_beneficiarios(id_titular)
        self.legacy_repository.desactivar_preplanliga(tipo, documento)

        num_incle = self.legacy_repository.marcar_registros_incle(tipo, documento)
        for tipo_b, documento_b in beneficiarios_desactivados:
            num_incle += self.legacy_repository.marcar_registros_incle(tipo_b, documento_b)

        return DesactivacionTitularResultado(
            titular=TitularDetalle(**fila),
            beneficiarios_desactivados=len(beneficiarios_desactivados),
            registros_incle_marcados=num_incle,
        )

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

    def listar_nombres_planes(self) -> list[PlanNombre]:
        return [PlanNombre(**fila) for fila in self.repository.listar_nombres_planes()]
