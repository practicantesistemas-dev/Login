from app.models import Bitacora, Contacto, Oportunidad, PlanLiga, PlanLigaTipoPlan, Usuario
from app.modules.administracion.bitacora.repository import BitacoraRepository
from app.modules.administracion.bitacora.schemas import BitacoraCreate, BitacoraItem, BitacoraListado
from app.shared.enums import TipoActividadBitacora
from sqlalchemy.orm import Session


def _nombre_contacto(contacto: Contacto | None) -> str | None:
    if contacto is None:
        return None
    partes = [contacto.nombre1, contacto.apellido1]
    return " ".join(parte for parte in partes if parte)


def _item(
    bitacora: Bitacora,
    contacto: Contacto | None,
    usuario: Usuario | None,
    oportunidad: Oportunidad | None,
    servicio_oportunidad: PlanLigaTipoPlan | None,
    titular: PlanLiga | None,
    tipo_plan_titular: PlanLigaTipoPlan | None,
) -> BitacoraItem:
    plan_nombre = servicio_oportunidad.nombre if servicio_oportunidad else None
    if plan_nombre is None and tipo_plan_titular is not None:
        plan_nombre = tipo_plan_titular.nombre

    return BitacoraItem(
        id=bitacora.id,
        tipo=bitacora.tipo,
        descripcion=bitacora.descripcion,
        proximo_paso=bitacora.proximo_paso,
        fecha=bitacora.fecha,
        estado=bitacora.estado,
        usuario_id=bitacora.usuario_id,
        usuario_nombre=usuario.nombres if usuario else None,
        contacto_id=bitacora.contacto_id,
        contacto_nombre=_nombre_contacto(contacto),
        nombre_empresa=bitacora.nombre_empresa,
        oportunidad_id=bitacora.oportunidad_id,
        titular_id=bitacora.titular_id,
        plan_nombre=plan_nombre,
    )


class BitacoraService:
    def __init__(self, db: Session) -> None:
        self.repository = BitacoraRepository(db)

    def create(self, data: BitacoraCreate, username: str) -> Bitacora:
        bitacora = Bitacora(
            **data.model_dump(), usuario_id=self.repository.obtener_usuario_id(username)
        )
        return self.repository.create(bitacora)

    def listar(
        self,
        tipo: TipoActividadBitacora | None = None,
        q: str | None = None,
        contacto_id: int | None = None,
        oportunidad_id: int | None = None,
        titular_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> BitacoraListado:
        filas, total = self.repository.listar(
            tipo=tipo.value if tipo else None,
            q=q,
            contacto_id=contacto_id,
            oportunidad_id=oportunidad_id,
            titular_id=titular_id,
            skip=skip,
            limit=limit,
        )
        conteo = self.repository.conteo_por_tipo(
            contacto_id=contacto_id,
            oportunidad_id=oportunidad_id,
            titular_id=titular_id,
        )

        return BitacoraListado(
            items=[_item(*fila) for fila in filas],
            total=total,
            conteo_por_tipo={tipo_valor: cantidad for tipo_valor, cantidad in conteo if tipo_valor},
        )
