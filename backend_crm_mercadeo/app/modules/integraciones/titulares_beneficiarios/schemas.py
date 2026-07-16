from pydantic import BaseModel
from typing import Optional

class ResumenTitularesBeneficiarios(BaseModel):
    titulares_activos: int
    beneficiarios_activos: int


class PlanItem(BaseModel):
    ID: int
    NOMBRE: str
    CATEGORIA: Optional[str] = None
    TIPO: Optional[str] = None
    MAX_BENEFICIARIOS: Optional[int] = None
    DESCRIPCION: Optional[str] = None
    ESTADO: bool


class ListadoTitulares(BaseModel):
    ID_TITULAR: int
    TITULAR: str
    EMAIL: Optional[str] = None
    TELEFONO: Optional[str] = None
    TIPO_DOCUMENTO: Optional[str] = None
    DOCUMENTO: str
    EMPRESA: Optional[str] = None
    PLANES: str
    BENEFICIARIOS: str
    INSCRIPCION: Optional[str] = None
    ESTADO: str