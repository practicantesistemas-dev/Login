from sqlalchemy import func, or_, select
from sqlalchemy.sql.elements import ColumnElement

from app.models import Proveedor
from app.shared.database.base_repository import BaseRepository


class ProveedorRepository(BaseRepository[Proveedor]):
    model = Proveedor

    def _filtros(
        self,
        q: str | None,
        estado: bool | None,
        categoria: str | None,
    ) -> list[ColumnElement]:
        condiciones = []
        if estado is not None:
            condiciones.append(Proveedor.estado == estado)
        if categoria is not None:
            condiciones.append(func.upper(Proveedor.categoria) == categoria.upper())
        if q:
            patron = f"%{q.strip().upper()}%"
            condiciones.append(
                or_(
                    func.upper(Proveedor.nombre).like(patron),
                    func.upper(Proveedor.nit).like(patron),
                    func.upper(Proveedor.correo).like(patron),
                    func.upper(Proveedor.categoria).like(patron),
                )
            )
        return condiciones

    def buscar(
        self,
        q: str | None = None,
        estado: bool | None = None,
        categoria: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Proveedor]:
        condiciones = self._filtros(q, estado, categoria)
        stmt = (
            select(Proveedor)
            .where(*condiciones)
            .order_by(Proveedor.nombre)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def contar(
        self,
        q: str | None = None,
        estado: bool | None = None,
        categoria: str | None = None,
    ) -> int:
        condiciones = self._filtros(q, estado, categoria)
        stmt = select(func.count()).select_from(Proveedor).where(*condiciones)
        return self.db.scalar(stmt) or 0

    def categorias(self) -> list[str]:
        stmt = (
            select(Proveedor.categoria)
            .where(Proveedor.categoria.is_not(None))
            .distinct()
            .order_by(Proveedor.categoria)
        )
        return [categoria for categoria in self.db.scalars(stmt) if categoria]
