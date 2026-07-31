from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.modules.marketing.etiquetas.schemas import EtiquetaRead
from app.shared.enums import TipoContacto


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
    responsable_id: int | None = None


class ContactoCreate(ContactoBase):
    etiqueta_ids: list[int] = []


class ContactoRead(ContactoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None
    etiquetas: list[EtiquetaRead] = []
