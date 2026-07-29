from sqlalchemy.orm import Session

from app.modules.compartidos.ubicaciones.repository import UbicacionesRepository
from app.modules.compartidos.ubicaciones.schemas import DepartamentoItem, MunicipioItem


class UbicacionesService:
    def __init__(self, db: Session) -> None:
        self.repository = UbicacionesRepository(db)

    def listar_departamentos(self, q: str | None = None) -> list[DepartamentoItem]:
        filas = self.repository.listar_departamentos(q)
        return [DepartamentoItem(**fila) for fila in filas]

    def listar_municipios(
        self, departamento: str | None = None, q: str | None = None
    ) -> list[MunicipioItem]:
        filas = self.repository.listar_municipios(departamento, q)
        return [MunicipioItem(**fila) for fila in filas]
