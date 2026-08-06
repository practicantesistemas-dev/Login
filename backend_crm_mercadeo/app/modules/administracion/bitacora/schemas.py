from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.shared.enums import EstadoBitacora, TipoActividadBitacora


class BitacoraCreate(BaseModel):
    tipo: TipoActividadBitacora
    descripcion: str
    proximo_paso: str | None = None
    fecha: datetime | None = None
    contacto_id: int | None = None
    nombre_empresa: str | None = None
    oportunidad_id: int | None = None
    titular_id: int | None = None
    estado: EstadoBitacora = EstadoBitacora.REALIZADO

    @model_validator(mode="after")
    def validar_referencia(self) -> "BitacoraCreate":
        if not any((self.contacto_id, self.nombre_empresa, self.oportunidad_id, self.titular_id)):
            raise ValueError(
                "Debe indicar al menos un contacto, empresa, oportunidad o titular relacionado"
            )
        return self


class BitacoraUpdate(BaseModel):
    tipo: TipoActividadBitacora | None = None
    descripcion: str | None = None
    proximo_paso: str | None = None
    fecha: datetime | None = None
    contacto_id: int | None = None
    nombre_empresa: str | None = None
    oportunidad_id: int | None = None
    titular_id: int | None = None
    estado: EstadoBitacora | None = None


class BitacoraRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str | None = None
    descripcion: str | None = None
    proximo_paso: str | None = None
    fecha: datetime | None = None
    usuario_id: int | None = None
    contacto_id: int | None = None
    nombre_empresa: str | None = None
    oportunidad_id: int | None = None
    titular_id: int | None = None
    estado: EstadoBitacora


class BitacoraItem(BaseModel):
    id: int
    tipo: str | None = None
    descripcion: str | None = None
    proximo_paso: str | None = None
    fecha: datetime | None = None
    estado: EstadoBitacora | None = None
    usuario_id: int | None = None
    usuario_nombre: str | None = None
    contacto_id: int | None = None
    contacto_nombre: str | None = None
    nombre_empresa: str | None = None
    oportunidad_id: int | None = None
    titular_id: int | None = None
    plan_nombre: str | None = None


class BitacoraListado(BaseModel):
    items: list[BitacoraItem]
    total: int
    conteo_por_tipo: dict[str, int]
