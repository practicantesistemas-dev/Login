from sqlalchemy import func, or_, select
from sqlalchemy.sql.elements import ColumnElement

from app.models import Actividad
from app.shared.database.base_repository import BaseRepository


class ActividadRepository(BaseRepository[Actividad]):
    model = Actividad

    def _filtros(self, q: str | None, proveedor_id: int | None) -> list[ColumnElement]:
        condiciones = []
        if proveedor_id is not None:
            condiciones.append(Actividad.proveedor_id == proveedor_id)
        if q:
            patron = f"%{q.strip().upper()}%"
            condiciones.append(
                or_(
                    func.upper(Actividad.nombre).like(patron),
                    func.upper(Actividad.descripcion).like(patron),
                )
            )
        return condiciones

    def buscar(
        self,
        q: str | None = None,
        proveedor_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Actividad]:
        condiciones = self._filtros(q, proveedor_id)
        stmt = (
            select(Actividad)
            .where(*condiciones)
            .order_by(Actividad.fecha_creacion.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def contar(self, q: str | None = None, proveedor_id: int | None = None) -> int:
        condiciones = self._filtros(q, proveedor_id)
        stmt = select(func.count()).select_from(Actividad).where(*condiciones)
        return self.db.scalar(stmt) or 0
