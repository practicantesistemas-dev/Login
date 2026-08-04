from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActividadBase(BaseModel):
    nombre: str
    cantidad: float | None = None
    precio: float | None = None
    descripcion: str | None = None
    proveedor_id: int


class ActividadCreate(ActividadBase):
    pass


class ActividadUpdate(BaseModel):
    nombre: str | None = None
    cantidad: float | None = None
    precio: float | None = None
    descripcion: str | None = None
    proveedor_id: int | None = None


class ActividadRead(ActividadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None


class ActividadListado(BaseModel):
    items: list[ActividadRead]
    total: int
