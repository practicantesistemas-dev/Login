from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Proveedor
from app.modules.servicios_proveedores.proveedores.exceptions import ProveedorNotFoundError
from app.modules.servicios_proveedores.proveedores.repository import ProveedorRepository
from app.modules.servicios_proveedores.proveedores.schemas import (
    ProveedorCreate,
    ProveedorListado,
    ProveedorRead,
    ProveedorUpdate,
)


class ProveedorService:
    def __init__(self, db: Session) -> None:
        self.repository = ProveedorRepository(db)

    def list(
        self,
        q: str | None = None,
        estado: bool | None = None,
        categoria: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> ProveedorListado:
        proveedores = self.repository.buscar(
            q=q, estado=estado, categoria=categoria, skip=skip, limit=limit
        )
        total = self.repository.contar(q=q, estado=estado, categoria=categoria)
        return ProveedorListado(
            items=[ProveedorRead.model_validate(proveedor) for proveedor in proveedores],
            total=total,
        )

    def get(self, proveedor_id: int) -> Proveedor:
        proveedor = self.repository.get(proveedor_id)
        if proveedor is None:
            raise ProveedorNotFoundError(proveedor_id)
        return proveedor

    def categorias(self) -> list[str]:
        return self.repository.categorias()

    def create(self, data: ProveedorCreate) -> Proveedor:
        proveedor = Proveedor(**data.model_dump())
        return self.repository.create(proveedor)

    def update(self, proveedor_id: int, data: ProveedorUpdate) -> Proveedor:
        proveedor = self.get(proveedor_id)
        changes = data.model_dump(exclude_unset=True)
        return self.repository.update(proveedor, changes)

    def delete(self, proveedor_id: int) -> None:
        proveedor = self.get(proveedor_id)
        self.repository.delete(proveedor)
