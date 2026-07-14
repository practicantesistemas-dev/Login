from datetime import datetime

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.models import Bitacora, Contacto, Empresa, Oportunidad, PlanLiga, Servicio, TitularServicio

ESTADOS_OPORTUNIDAD_CERRADOS = {"ganada", "ganado", "perdida", "perdido", "cerrada", "cerrado"}
ESTADO_ACTIVO = "activo"
ESTADO_PLANLIGA_ACTIVO = "A"
ESTADO_BITACORA_PENDIENTE = "pendiente"


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

    def contar_contactos(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Contacto).where(
            *_rango(Contacto.fecha_creacion, desde, hasta)
        )
        return self.db.scalar(stmt) or 0

    def contar_empresas_vinculadas(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Empresa).where(
            Empresa.estado == True, *_rango(Empresa.fecha_creacion, desde, hasta)  # noqa: E712
        )
        return self.db.scalar(stmt) or 0

    def contar_oportunidades_en_curso(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Oportunidad).where(
            Oportunidad.estado.isnot(None),
            func.lower(Oportunidad.estado).notin_(ESTADOS_OPORTUNIDAD_CERRADOS),
            *_rango(Oportunidad.fecha_creacion, desde, hasta),
        )
        return self.db.scalar(stmt) or 0

    def contar_titulares_pl_activos(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(PlanLiga).where(
            PlanLiga.estado == ESTADO_PLANLIGA_ACTIVO,
            *_rango(PlanLiga.fecha_registro, desde, hasta),
        )
        return self.db.scalar(stmt) or 0

    def contar_servicios_plan_liga_activos(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count(func.distinct(TitularServicio.servicio_id))).where(
            func.lower(TitularServicio.estado) == ESTADO_ACTIVO,
            *_rango(TitularServicio.fecha_asignacion, desde, hasta),
        )
        return self.db.scalar(stmt) or 0

    def contar_seguimientos_pendientes(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Bitacora).where(
            func.lower(Bitacora.estado) == ESTADO_BITACORA_PENDIENTE,
            *_rango(Bitacora.fecha, desde, hasta),
        )
        return self.db.scalar(stmt) or 0

    def actividad_reciente(self, limit: int) -> list[tuple[Bitacora, Contacto | None, Empresa | None]]:
        stmt = (
            select(Bitacora, Contacto, Empresa)
            .outerjoin(Contacto, Bitacora.contacto_id == Contacto.id)
            .outerjoin(Empresa, Bitacora.empresa_id == Empresa.id)
            .order_by(Bitacora.fecha.desc())
            .limit(limit)
        )
        return [(row[0], row[1], row[2]) for row in self.db.execute(stmt).all()]

    def distribucion_contactos(self) -> list[tuple[str | None, int]]:
        stmt = (
            select(Contacto.estado, func.count())
            .group_by(Contacto.estado)
            .order_by(func.count().desc())
        )
        return list(self.db.execute(stmt).all())

    def top_servicios(self, limit: int) -> list[tuple[Servicio, int]]:
        conteo = (
            select(
                TitularServicio.servicio_id.label("servicio_id"),
                func.count(TitularServicio.id).label("total"),
            )
            .group_by(TitularServicio.servicio_id)
            .subquery()
        )
        stmt = (
            select(Servicio, conteo.c.total)
            .join(conteo, conteo.c.servicio_id == Servicio.id)
            .order_by(conteo.c.total.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).all())
