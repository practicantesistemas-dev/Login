from sqlalchemy import func, select

from app.models import Empresa, PlanLiga, Usuario
from app.shared.database.base_repository import BaseRepository


class EmpresaRepository(BaseRepository[Empresa]):
    model = Empresa

    def obtener_usuario_id(self, username: str) -> int | None:
        stmt = select(Usuario.id).where(
            func.upper(func.trim(Usuario.usuario)) == username.strip().upper()
        )
        return self.db.scalar(stmt)

    # intranet_planliga.empresa es texto libre (cada titular lo escribe a mano, sin
    # catalogo): agrupar por UPPER(TRIM(...)) colapsa variantes que solo difieren en
    # mayusculas/espacios (ej. "Bancolombia" y "BANCOLOMBIA ") en un solo nombre
    # representativo, sin intentar unificar variantes mas de fondo (ej. con/sin "S.A.").
    def nombres_empresa_planliga(self) -> list[str]:
        nombre = func.trim(PlanLiga.empresa)
        # Ojo: en Oracle '' (cadena vacia) se trata como NULL, asi que un filtro
        # "nombre != ''" nunca es verdadero para ninguna fila (compara contra NULL) y la
        # consulta no devolveria nada. TRIM ya convierte NULL y "solo espacios" en NULL,
        # asi que "nombre.isnot(None)" alcanza para filtrar ambos casos.
        stmt = (
            select(func.min(nombre))
            .where(nombre.isnot(None))
            .group_by(func.upper(nombre))
        )
        return [n for n in self.db.scalars(stmt) if n]

    def razones_sociales_existentes(self) -> set[str]:
        stmt = select(func.upper(func.trim(Empresa.razon_social)))
        return {r for r in self.db.scalars(stmt) if r}
