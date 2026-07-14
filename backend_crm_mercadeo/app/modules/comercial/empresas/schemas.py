from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmpresaBase(BaseModel):
    razon_social: str
    nit: str
    industria: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    estado: bool = True
    responsable_id: int | None = None


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaUpdate(BaseModel):
    razon_social: str | None = None
    nit: str | None = None
    industria: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    estado: bool | None = None
    responsable_id: int | None = None


class EmpresaRead(EmpresaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None
