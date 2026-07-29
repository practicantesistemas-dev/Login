from sqlalchemy import String, and_, column, func, or_, select, table
from sqlalchemy.orm import Session

# INDEP/INMUN son catalogos externos (divipola) del sistema Intranet, sin
# relacion con otras tablas del CRM, por eso se declaran como tablas livianas
# (sin clase ORM completa) en vez de agregarlas a app/models.py.
indep = table(
    "indep",
    column("depcod", String),
    column("depnom", String),
    column("depact", String),
)

inmun = table(
    "inmun",
    column("muncod", String),
    column("munnom", String),
    column("mundep", String),
    column("munact", String),
)


class UbicacionesRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar_departamentos(self, q: str | None) -> list[dict]:
        condiciones = [indep.c.depact == "S"]
        if q:
            condiciones.append(func.upper(indep.c.depnom).like(f"%{q.upper()}%"))

        stmt = (
            select(
                indep.c.depcod.label("CODIGO"),
                indep.c.depnom.label("NOMBRE"),
            )
            .where(and_(*condiciones))
            .order_by(indep.c.depnom)
        )
        return [dict(fila) for fila in self.db.execute(stmt).mappings().all()]

    def listar_municipios(self, departamento: str | None, q: str | None) -> list[dict]:
        condiciones = [inmun.c.munact == "S"]
        if departamento:
            condiciones.append(
                or_(
                    indep.c.depcod == departamento,
                    func.upper(indep.c.depnom).like(f"%{departamento.upper()}%"),
                )
            )
        if q:
            condiciones.append(func.upper(inmun.c.munnom).like(f"%{q.upper()}%"))

        stmt = (
            select(
                inmun.c.muncod.label("CODIGO"),
                inmun.c.munnom.label("NOMBRE"),
                indep.c.depcod.label("DEPARTAMENTO_CODIGO"),
                indep.c.depnom.label("DEPARTAMENTO_NOMBRE"),
            )
            .select_from(inmun)
            .join(indep, indep.c.depcod == inmun.c.mundep)
            .where(and_(*condiciones))
            .order_by(indep.c.depnom, inmun.c.munnom)
        )
        return [dict(fila) for fila in self.db.execute(stmt).mappings().all()]
