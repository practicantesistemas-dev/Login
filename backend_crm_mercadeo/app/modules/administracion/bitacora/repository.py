from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models import Bitacora, Contacto, Oportunidad, PlanLiga, PlanLigaTipoPlan, Usuario
from app.shared.database.base_repository import BaseRepository

ServicioOportunidad = aliased(PlanLigaTipoPlan)
TipoPlanTitular = aliased(PlanLigaTipoPlan)


class BitacoraRepository(BaseRepository[Bitacora]):
    model = Bitacora

    def _query_base(self):
        return (
            select(Bitacora, Contacto, Usuario, Oportunidad, ServicioOportunidad, PlanLiga, TipoPlanTitular)
            .outerjoin(Contacto, Bitacora.contacto_id == Contacto.id)
            .outerjoin(Usuario, Bitacora.usuario_id == Usuario.id)
            .outerjoin(Oportunidad, Bitacora.oportunidad_id == Oportunidad.id)
            .outerjoin(ServicioOportunidad, Oportunidad.servicio_id == ServicioOportunidad.id)
            .outerjoin(PlanLiga, Bitacora.titular_id == PlanLiga.id)
            .outerjoin(TipoPlanTitular, PlanLiga.tipo_plan_id == TipoPlanTitular.id)
        )

    def _filtros(
        self,
        tipo: str | None,
        q: str | None,
        contacto_id: int | None,
        oportunidad_id: int | None,
        titular_id: int | None,
    ) -> list:
        condiciones = []
        if tipo is not None:
            condiciones.append(Bitacora.tipo == tipo)
        if contacto_id is not None:
            condiciones.append(Bitacora.contacto_id == contacto_id)
        if oportunidad_id is not None:
            condiciones.append(Bitacora.oportunidad_id == oportunidad_id)
        if titular_id is not None:
            condiciones.append(Bitacora.titular_id == titular_id)
        if q:
            patron = f"%{q.upper()}%"
            condiciones.append(
                or_(
                    func.upper(Contacto.nombre1).like(patron),
                    func.upper(Contacto.apellido1).like(patron),
                    func.upper(Bitacora.nombre_empresa).like(patron),
                    func.upper(Bitacora.descripcion).like(patron),
                )
            )
        return condiciones

    def listar(
        self,
        tipo: str | None = None,
        q: str | None = None,
        contacto_id: int | None = None,
        oportunidad_id: int | None = None,
        titular_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list, int]:
        condiciones = self._filtros(tipo, q, contacto_id, oportunidad_id, titular_id)

        total = self.db.scalar(
            select(func.count()).select_from(self._query_base().where(*condiciones).subquery())
        ) or 0

        stmt = (
            self._query_base()
            .where(*condiciones)
            .order_by(Bitacora.fecha.desc())
            .offset(skip)
            .limit(limit)
        )
        filas = list(self.db.execute(stmt).all())
        return filas, total

    def obtener_usuario_id(self, username: str) -> int | None:
        stmt = select(Usuario.id).where(
            func.upper(func.trim(Usuario.usuario)) == username.strip().upper()
        )
        return self.db.scalar(stmt)

    def conteo_por_tipo(
        self,
        contacto_id: int | None = None,
        oportunidad_id: int | None = None,
        titular_id: int | None = None,
    ) -> list[tuple[str | None, int]]:
        condiciones = self._filtros(None, None, contacto_id, oportunidad_id, titular_id)
        stmt = (
            select(Bitacora.tipo, func.count(Bitacora.id))
            .where(*condiciones)
            .group_by(Bitacora.tipo)
        )
        return list(self.db.execute(stmt).all())
