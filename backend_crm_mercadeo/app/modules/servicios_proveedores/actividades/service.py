from sqlalchemy.orm import Session

from app.models import Actividad
from app.modules.servicios_proveedores.actividades.exceptions import ActividadNotFoundError
from app.modules.servicios_proveedores.actividades.repository import ActividadRepository
from app.modules.servicios_proveedores.actividades.schemas import (
    ActividadCreate,
    ActividadListado,
    ActividadRead,
    ActividadUpdate,
)


class ActividadService:
    def __init__(self, db: Session) -> None:
        self.repository = ActividadRepository(db)

    def list(
        self,
        q: str | None = None,
        proveedor_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> ActividadListado:
        actividades = self.repository.buscar(
            q=q, proveedor_id=proveedor_id, skip=skip, limit=limit
        )
        total = self.repository.contar(q=q, proveedor_id=proveedor_id)
        return ActividadListado(
            items=[ActividadRead.model_validate(actividad) for actividad in actividades],
            total=total,
        )

    def get(self, actividad_id: int) -> Actividad:
        actividad = self.repository.get(actividad_id)
        if actividad is None:
            raise ActividadNotFoundError(actividad_id)
        return actividad

    def create(self, data: ActividadCreate) -> Actividad:
        actividad = Actividad(**data.model_dump())
        return self.repository.create(actividad)

    def update(self, actividad_id: int, data: ActividadUpdate) -> Actividad:
        actividad = self.get(actividad_id)
        changes = data.model_dump(exclude_unset=True)
        return self.repository.update(actividad, changes)

    def delete(self, actividad_id: int) -> None:
        actividad = self.get(actividad_id)
        self.repository.delete(actividad)
