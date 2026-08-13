from sqlalchemy.orm import Session

from app.models import Contacto, Empresa, EtapaEmbudo, Oportunidad, PlanLiga, Usuario
from app.modules.comercial.oportunidades.exceptions import (
    EtapaEmbudoNoConfiguradaError,
    OportunidadNotFoundError,
)
from app.modules.comercial.oportunidades.repository import OportunidadRepository
from app.modules.comercial.oportunidades.schemas import (
    OportunidadContactoResumen,
    OportunidadCreate,
    OportunidadEmpresaResumen,
    OportunidadRead,
    OportunidadResponsableResumen,
    OportunidadTitularResumen,
    OportunidadUpdate,
    TipoCliente,
)
from app.shared.enums import EtapaEmbudoNombre

ESTADOS_CERRADOS = {EtapaEmbudoNombre.GANADA, EtapaEmbudoNombre.PERDIDA}


def _tipo_cliente(oportunidad: Oportunidad) -> TipoCliente:
    if oportunidad.plan_liga_titular_id is not None:
        return "titular"
    if oportunidad.empresa_id is not None:
        return "empresa"
    return "contacto"


def _estado_de_etapa(etapa: EtapaEmbudoNombre) -> str:
    return etapa.value if etapa in ESTADOS_CERRADOS else "Abierta"


def _item(
    fila: tuple[Oportunidad, Empresa | None, Contacto | None, PlanLiga | None, Usuario | None, EtapaEmbudo | None],
) -> OportunidadRead:
    oportunidad, empresa, contacto, titular, responsable, etapa = fila
    return OportunidadRead(
        id=oportunidad.id,
        tipo_cliente=_tipo_cliente(oportunidad),
        empresa_id=oportunidad.empresa_id,
        contacto_id=oportunidad.contacto_id,
        plan_liga_titular_id=oportunidad.plan_liga_titular_id,
        servicio_nombre=oportunidad.servicio_nombre,
        responsable_id=oportunidad.responsable_id,
        valor=oportunidad.valor,
        probabilidad=oportunidad.probabilidad,
        estado=oportunidad.estado,
        etapa=EtapaEmbudoNombre(etapa.nombre) if etapa is not None else None,
        fecha_creacion=oportunidad.fecha_creacion,
        fecha_actualizacion=oportunidad.fecha_actualizacion,
        empresa=OportunidadEmpresaResumen.model_validate(empresa) if empresa is not None else None,
        contacto=OportunidadContactoResumen.model_validate(contacto) if contacto is not None else None,
        titular=OportunidadTitularResumen.model_validate(titular) if titular is not None else None,
        responsable=(
            OportunidadResponsableResumen.model_validate(responsable) if responsable is not None else None
        ),
    )


class OportunidadService:
    def __init__(self, db: Session) -> None:
        self.repository = OportunidadRepository(db)

    def listar(self, skip: int = 0, limit: int = 100) -> list[OportunidadRead]:
        filas = self.repository.listar(skip=skip, limit=limit)
        return [_item(fila) for fila in filas]

    def obtener(self, oportunidad_id: int) -> OportunidadRead:
        fila = self.repository.obtener_con_relaciones(oportunidad_id)
        if fila is None:
            raise OportunidadNotFoundError(oportunidad_id)
        return _item(fila)

    def _resolver_etapa_id(self, etapa: EtapaEmbudoNombre) -> int:
        etapa_id = self.repository.obtener_etapa_id(etapa)
        if etapa_id is None:
            raise EtapaEmbudoNoConfiguradaError(etapa.value)
        return etapa_id

    # responsable_id no llega en el body: el responsable es quien crea la oportunidad, resuelto
    # a partir del Bearer token (mismo patron que POST /api/contactos/ y /api/bitacora/).
    def crear(self, data: OportunidadCreate, username: str) -> OportunidadRead:
        etapa_id = self._resolver_etapa_id(data.etapa)
        oportunidad = Oportunidad(
            empresa_id=data.empresa_id,
            contacto_id=data.contacto_id,
            plan_liga_titular_id=data.plan_liga_titular_id,
            servicio_nombre=data.servicio_nombre,
            valor=data.valor,
            probabilidad=data.probabilidad,
            etapa_id=etapa_id,
            estado=_estado_de_etapa(data.etapa),
            responsable_id=self.repository.obtener_usuario_id(username),
        )
        oportunidad = self.repository.create(oportunidad)
        return self.obtener(oportunidad.id)

    def actualizar(self, oportunidad_id: int, data: OportunidadUpdate) -> OportunidadRead:
        oportunidad = self.repository.get(oportunidad_id)
        if oportunidad is None:
            raise OportunidadNotFoundError(oportunidad_id)

        cambios = data.model_dump(exclude_unset=True, exclude={"etapa"})
        if data.etapa is not None:
            cambios["etapa_id"] = self._resolver_etapa_id(data.etapa)
            cambios["estado"] = _estado_de_etapa(data.etapa)

        if cambios:
            self.repository.update(oportunidad, cambios)
        return self.obtener(oportunidad_id)

    def eliminar(self, oportunidad_id: int) -> None:
        oportunidad = self.repository.get(oportunidad_id)
        if oportunidad is None:
            raise OportunidadNotFoundError(oportunidad_id)
        self.repository.delete(oportunidad)
