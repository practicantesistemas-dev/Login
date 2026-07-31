from pydantic import BaseModel, ConfigDict


class EtiquetaBase(BaseModel):
    nombre: str
    color: str


class EtiquetaCreate(EtiquetaBase):
    pass


class EtiquetaRead(EtiquetaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
