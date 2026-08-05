import logging
from datetime import datetime

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import (
    Bitacora,
    Contacto,
    EtapaEmbudo,
    Oportunidad,
    PlanLiga,
    PlanLigaTipoPlan,
    Usuario,
)
from app.shared.enums import EstadoBitacora, TipoContacto

ESTADOS_OPORTUNIDAD_CERRADOS = {"ganada", "ganado", "perdida", "perdido", "cerrada", "cerrado"}
ESTADO_ACTIVO = "activo"
ESTADO_PLANLIGA_ACTIVO = "A"

logger = logging.getLogger(__name__)


def _rango(campo_fecha: ColumnElement, desde: datetime | None, hasta: datetime | None) -> list:
    condiciones = []
    if desde is not None:
        condiciones.append(campo_fecha >= desde)
    if hasta is not None:
        condiciones.append(campo_fecha < hasta)
    return condiciones


class TableroRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _contar_seguro(self, stmt) -> int:
        """Ejecuta un SELECT count() devolviendo 0 si la tabla/consulta falla
        (ej. ORA-00942 tabla no existe), en vez de tumbar todo el resumen."""
        try:
            return self.db.scalar(stmt) or 0
        except SQLAlchemyError:
            logger.warning("Fallo al contar para el tablero, se usa 0", exc_info=True)
            self.db.rollback()
            return 0

    def contar_contactos(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Contacto).where(
            *_rango(Contacto.fecha_creacion, desde, hasta)
        )
        return self._contar_seguro(stmt)

    def contar_oportunidades_en_curso(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Oportunidad).where(
            Oportunidad.estado.isnot(None),
            func.lower(Oportunidad.estado).notin_(ESTADOS_OPORTUNIDAD_CERRADOS),
            *_rango(Oportunidad.fecha_creacion, desde, hasta),
        )
        return self._contar_seguro(stmt)

    def contar_titulares_pl_activos(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(PlanLiga).where(
            PlanLiga.estado == ESTADO_PLANLIGA_ACTIVO,
            *_rango(PlanLiga.fecha_registro, desde, hasta),
        )
        return self._contar_seguro(stmt)

    def contar_servicios_plan_liga_activos(self) -> int:
        stmt = select(func.count(func.distinct(PlanLigaTipoPlan.categoria))).where(
            PlanLigaTipoPlan.estado == ESTADO_PLANLIGA_ACTIVO,
            PlanLigaTipoPlan.categoria.isnot(None),
        )
        return self._contar_seguro(stmt)

    def contar_seguimientos_pendientes(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Bitacora).where(
            Bitacora.estado == EstadoBitacora.PENDIENTE,
            *_rango(Bitacora.fecha, desde, hasta),
        )
        return self._contar_seguro(stmt)

    def actividad_reciente(
        self, limit: int
    ) -> list[tuple[Bitacora, Contacto | None, Usuario | None, PlanLiga | None]]:
        stmt = (
            select(Bitacora, Contacto, Usuario, PlanLiga)
            .outerjoin(Contacto, Bitacora.contacto_id == Contacto.id)
            .outerjoin(Usuario, Bitacora.usuario_id == Usuario.id)
            .outerjoin(PlanLiga, Bitacora.titular_id == PlanLiga.id)
            .order_by(Bitacora.fecha.desc())
            .limit(limit)
        )
        try:
            return [(row[0], row[1], row[2], row[3]) for row in self.db.execute(stmt).all()]
        except SQLAlchemyError:
            logger.warning("Fallo al cargar la actividad reciente, se usa lista vacia", exc_info=True)
            self.db.rollback()
            return []

    def contar_total_contactos(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Contacto).where(
            *_rango(Contacto.fecha_creacion, desde, hasta)
        )
        return self.db.scalar(stmt) or 0

    def contar_contactos_inactivos(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Contacto).where(
            or_(Contacto.estado.is_(None), func.lower(Contacto.estado) != ESTADO_ACTIVO),
            *_rango(Contacto.fecha_creacion, desde, hasta),
        )
        return self.db.scalar(stmt) or 0

    def contar_prospectos_activos(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Contacto).where(
            Contacto.tipo_contacto == TipoContacto.PROSPECTO,
            func.lower(Contacto.estado) == ESTADO_ACTIVO,
            *_rango(Contacto.fecha_creacion, desde, hasta),
        )
        return self.db.scalar(stmt) or 0

    def contar_clientes_activos(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Contacto).where(
            Contacto.tipo_contacto == TipoContacto.CLIENTE,
            func.lower(Contacto.estado) == ESTADO_ACTIVO,
            *_rango(Contacto.fecha_creacion, desde, hasta),
        )
        return self.db.scalar(stmt) or 0

    def embudo_comercial(
        self,
        embudo_id: int | None,
        desde: datetime | None,
        hasta: datetime | None,
    ) -> list[tuple[EtapaEmbudo, int]]:
        conteo = (
            select(
                Oportunidad.etapa_id.label("etapa_id"),
                func.count(Oportunidad.id).label("total"),
            )
            .where(*_rango(Oportunidad.fecha_creacion, desde, hasta))
            .group_by(Oportunidad.etapa_id)
            .subquery()
        )
        stmt = (
            select(EtapaEmbudo, func.coalesce(conteo.c.total, 0))
            .outerjoin(conteo, conteo.c.etapa_id == EtapaEmbudo.id)
            .order_by(EtapaEmbudo.embudo_id, EtapaEmbudo.orden)
        )
        if embudo_id is not None:
            stmt = stmt.where(EtapaEmbudo.embudo_id == embudo_id)
        return list(self.db.execute(stmt).all())

    def top_planes(self, limit: int) -> list:
        nombre_plan = func.coalesce(PlanLigaTipoPlan.nombre, "Plan Estandar")
        stmt = (
            select(
                PlanLiga.tipo_plan_id.label("plan_id"),
                nombre_plan.label("nombre"),
                func.count(PlanLiga.id).label("total"),
            )
            .select_from(PlanLiga)
            .outerjoin(PlanLigaTipoPlan, PlanLigaTipoPlan.id == PlanLiga.tipo_plan_id)
            .where(*self._filtro_planes_activos())
            .group_by(PlanLiga.tipo_plan_id, PlanLigaTipoPlan.nombre)
            .order_by(func.count(PlanLiga.id).desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).all())

    def _filtro_planes_activos(self) -> list:
        return [
            PlanLiga.estado == ESTADO_PLANLIGA_ACTIVO,
            or_(
                PlanLiga.tipo_plan_id.is_(None),
                PlanLigaTipoPlan.estado == ESTADO_PLANLIGA_ACTIVO,
            ),
        ]

    def contar_planes_activos(self) -> int:
        stmt = (
            select(func.count(PlanLiga.id))
            .select_from(PlanLiga)
            .outerjoin(PlanLigaTipoPlan, PlanLigaTipoPlan.id == PlanLiga.tipo_plan_id)
            .where(*self._filtro_planes_activos())
        )
        return self.db.scalar(stmt) or 0
