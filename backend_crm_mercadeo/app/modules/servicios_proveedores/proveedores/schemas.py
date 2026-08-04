from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProveedorBase(BaseModel):
    nombre: str
    categoria: str | None = None
    nit: str | None = None
    correo: str | None = None
    telefono: str | None = None
    estado: bool = True


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: str | None = None
    categoria: str | None = None
    nit: str | None = None
    correo: str | None = None
    telefono: str | None = None
    estado: bool | None = None


class ProveedorRead(ProveedorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None


class ProveedorListado(BaseModel):
    items: list[ProveedorRead]
    total: int
