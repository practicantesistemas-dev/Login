from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.shared.enums import EstadoBitacora, TipoActividadBitacora


class BitacoraCreate(BaseModel):
    tipo: TipoActividadBitacora
    descripcion: str
    proximo_paso: str | None = None
    fecha: datetime | None = None
    usuario_id: int | None = None
    contacto_id: int | None = None
    empresa_id: int | None = None
    oportunidad_id: int | None = None
    titular_id: int | None = None
    estado: EstadoBitacora = EstadoBitacora.REALIZADO

    @model_validator(mode="after")
    def validar_referencia(self) -> "BitacoraCreate":
        if not any((self.contacto_id, self.empresa_id, self.oportunidad_id, self.titular_id)):
            raise ValueError(
                "Debe indicar al menos un contacto, empresa, oportunidad o titular relacionado"
            )
        return self


class BitacoraRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str | None = None
    descripcion: str | None = None
    proximo_paso: str | None = None
    fecha: datetime | None = None
    usuario_id: int | None = None
    contacto_id: int | None = None
    empresa_id: int | None = None
    oportunidad_id: int | None = None
    titular_id: int | None = None
    estado: EstadoBitacora
