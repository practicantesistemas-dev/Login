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
    BENEFICIARIOS_ADICIONALES: Optional[int] = None
    DESCRIPCION: Optional[str] = None
    ESTADO: bool


class TitularDetalle(BaseModel):
    ID_TITULAR: int
    DOCUMENTO: Optional[str] = None
    TIPO_DOCUMENTO: Optional[str] = None
    NOMBRE1: Optional[str] = None
    NOMBRE2: Optional[str] = None
    APELLIDO1: Optional[str] = None
    APELLIDO2: Optional[str] = None
    FECHA_NACIMIENTO: Optional[str] = None
    SEXO: Optional[str] = None
    CORREO: Optional[str] = None
    TELEFONO: Optional[str] = None
    DIRECCION: Optional[str] = None
    CIUDAD: Optional[str] = None
    DEPARTAMENTO: Optional[str] = None
    TIPO_PLAN: Optional[str] = None
    TIPO_AFILIADO: Optional[str] = None
    EMPRESA: Optional[str] = None
    EPS: Optional[str] = None
    OTRAEPS: Optional[str] = None
    PLAN_SALUD: Optional[str] = None
    PLAN_NOMBRE: Optional[str] = None
    ESTADO: Optional[str] = None
    FECHA_INGRESO: Optional[str] = None


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