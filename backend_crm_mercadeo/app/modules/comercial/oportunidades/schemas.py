from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.shared.enums import EtapaEmbudoNombre

TipoCliente = Literal["empresa", "contacto", "titular"]


class OportunidadEmpresaResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    razon_social: str
    ciudad: str | None = None


class OportunidadContactoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre1: str
    apellido1: str | None = None
    cargo: str | None = None


class OportunidadTitularResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre1: str | None = None
    nombre2: str | None = None
    apellido1: str | None = None
    apellido2: str | None = None
    empresa: str | None = None


class OportunidadResponsableResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombres: str | None = None


class OportunidadBase(BaseModel):
    empresa_id: int | None = None
    contacto_id: int | None = None
    plan_liga_titular_id: int | None = None
    servicio_nombre: str | None = None
    valor: float | None = None
    probabilidad: float | None = None


class OportunidadCreate(OportunidadBase):
    etapa: EtapaEmbudoNombre = EtapaEmbudoNombre.LEAD


class OportunidadUpdate(BaseModel):
    empresa_id: int | None = None
    contacto_id: int | None = None
    plan_liga_titular_id: int | None = None
    servicio_nombre: str | None = None
    valor: float | None = None
    probabilidad: float | None = None
    etapa: EtapaEmbudoNombre | None = None


class OportunidadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_cliente: TipoCliente
    empresa_id: int | None = None
    contacto_id: int | None = None
    plan_liga_titular_id: int | None = None
    servicio_nombre: str | None = None
    responsable_id: int | None = None
    valor: float | None = None
    probabilidad: float | None = None
    estado: str | None = None
    etapa: EtapaEmbudoNombre | None = None
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None
    empresa: OportunidadEmpresaResumen | None = None
    contacto: OportunidadContactoResumen | None = None
    titular: OportunidadTitularResumen | None = None
    responsable: OportunidadResponsableResumen | None = None
