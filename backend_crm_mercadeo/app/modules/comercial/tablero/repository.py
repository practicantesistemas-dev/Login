from datetime import datetime

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import Session

from app.models import (
    Bitacora,
    Contacto,
    Empresa,
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
        stmt = select(func.count(func.distinct(PlanLiga.tipo_plan_id))).where(
            PlanLiga.estado == ESTADO_PLANLIGA_ACTIVO,
            PlanLiga.tipo_plan_id.isnot(None),
            *_rango(PlanLiga.fecha_registro, desde, hasta),
        )
        return self.db.scalar(stmt) or 0

    def contar_seguimientos_pendientes(self, desde: datetime | None, hasta: datetime | None) -> int:
        stmt = select(func.count()).select_from(Bitacora).where(
            Bitacora.estado == EstadoBitacora.PENDIENTE,
            *_rango(Bitacora.fecha, desde, hasta),
        )
        return self.db.scalar(stmt) or 0

    def actividad_reciente(
        self, limit: int
    ) -> list[tuple[Bitacora, Contacto | None, Empresa | None, Usuario | None]]:
        stmt = (
            select(Bitacora, Contacto, Empresa, Usuario)
            .outerjoin(Contacto, Bitacora.contacto_id == Contacto.id)
            .outerjoin(Empresa, Bitacora.empresa_id == Empresa.id)
            .outerjoin(Usuario, Bitacora.usuario_id == Usuario.id)
            .order_by(Bitacora.fecha.desc())
            .limit(limit)
        )
        return [(row[0], row[1], row[2], row[3]) for row in self.db.execute(stmt).all()]

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
            .group_by(PlanLiga.tipo_plan_id, PlanLigaTipoPlan.nombre)
            .order_by(func.count(PlanLiga.id).desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).all())
