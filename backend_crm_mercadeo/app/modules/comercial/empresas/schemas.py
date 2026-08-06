from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmpresaBase(BaseModel):
    razon_social: str
    nit: str
    industria: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    estado: bool = True


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaUpdate(BaseModel):
    razon_social: str | None = None
    nit: str | None = None
    industria: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    estado: bool | None = None


class EmpresaRead(EmpresaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    responsable_id: int | None = None
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None
