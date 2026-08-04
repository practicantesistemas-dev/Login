from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.modules.marketing.etiquetas.schemas import EtiquetaRead
from app.shared.enums import TipoContacto


class ContactoEmpresaResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    razon_social: str
    nit: str
    ciudad: str | None = None


class ContactoResponsableResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombres: str | None = None
    usuario: str | None = None


class ContactoBase(BaseModel):
    tipo_contacto: TipoContacto | None = None
    tipo_documento: str | None = None
    documento: str | None = None
    nombre1: str
    nombre2: str | None = None
    apellido1: str | None = None
    apellido2: str | None = None
    sexo: str | None = None
    correo: str | None = None
    telefono: str | None = None
    cargo: str | None = None
    municipio: str | None = None
    departamento: str | None = None
    fecha_nacimiento: date | None = None
    estado: str | None = None
    empresa_id: int | None = None


class ContactoCreate(ContactoBase):
    etiqueta_ids: list[int] = []


class ContactoUpdate(BaseModel):
    tipo_contacto: TipoContacto | None = None
    tipo_documento: str | None = None
    documento: str | None = None
    nombre1: str | None = None
    nombre2: str | None = None
    apellido1: str | None = None
    apellido2: str | None = None
    sexo: str | None = None
    correo: str | None = None
    telefono: str | None = None
    cargo: str | None = None
    municipio: str | None = None
    departamento: str | None = None
    fecha_nacimiento: date | None = None
    estado: str | None = None
    empresa_id: int | None = None
    etiqueta_ids: list[int] | None = None


class ContactoRead(ContactoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    responsable_id: int | None = None
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None
    etiquetas: list[EtiquetaRead] = []
    empresa: ContactoEmpresaResumen | None = None
    responsable: ContactoResponsableResumen | None = None
