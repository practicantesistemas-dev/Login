from datetime import date

from pydantic import BaseModel
from typing import Optional

class ResumenTitularesBeneficiarios(BaseModel):
    titulares_activos: int
    beneficiarios_activos: int


class PlanItem(BaseModel):
    ID: int
    NOMBRE: str
    TIPO: Optional[str] = None
    MAX_BENEFICIARIOS: Optional[int] = None
    BENEFICIARIOS_ADICIONALES: Optional[int] = None
    DESCRIPCION: Optional[str] = None
    ESTADO: Optional[str] = None


class PlanNombre(BaseModel):
    ID: int
    NOMBRE: str


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
    PLANES: Optional[str] = None
    BENEFICIARIOS: Optional[str] = None
    INSCRIPCION: Optional[str] = None
    ESTADO: str


class TitularUpdate(BaseModel):
    DOCUMENTO: Optional[str] = None
    TIPO_DOCUMENTO: Optional[str] = None
    NOMBRE1: Optional[str] = None
    NOMBRE2: Optional[str] = None
    APELLIDO1: Optional[str] = None
    APELLIDO2: Optional[str] = None
    FECHA_NACIMIENTO: Optional[date] = None
    SEXO: Optional[str] = None
    CORREO: Optional[str] = None
    TELEFONO: Optional[str] = None
    DIRECCION: Optional[str] = None
    CIUDAD: Optional[str] = None
    DEPARTAMENTO: Optional[str] = None
    EMPRESA: Optional[str] = None
    ESTADO: Optional[str] = None


class TitularActivar(BaseModel):
    FECHA_INGRESO: date


class TitularCrear(BaseModel):
    TIPO_PLAN: Optional[str] = None
    TIPO_DOCUMENTO: str
    DOCUMENTO: str
    NOMBRE1: str
    NOMBRE2: Optional[str] = None
    APELLIDO1: str
    APELLIDO2: Optional[str] = None
    FECHA_NACIMIENTO: Optional[date] = None
    SEXO: Optional[str] = None
    DIRECCION: Optional[str] = None
    CIUDAD: Optional[str] = None
    DEPARTAMENTO: Optional[str] = None
    CORREO: Optional[str] = None
    TELEFONO: Optional[str] = None
    FECHA_INGRESO: date
    TIPO_AFILIADO: str
    EMPRESA: Optional[str] = None
    EPS: Optional[str] = None
    OTRAEPS: Optional[str] = None
    PLAN_SALUD: str
    PLAN_NOMBRE: str
    TIPO_PLAN_ID: Optional[int] = None


class CreacionTitularResultado(BaseModel):
    titular: TitularDetalle
    usuario_servinte_creado: bool
    marcado_en_incle: bool


class ActivacionTitularResultado(BaseModel):
    titular: TitularDetalle
    beneficiarios_activados: int
    registros_incle_desmarcados: int


class DesactivacionTitularResultado(BaseModel):
    titular: TitularDetalle
    beneficiarios_desactivados: int
    registros_incle_marcados: int


class ListadoTitularesPaginado(BaseModel):
    items: list[ListadoTitulares]
    total: int
    limit: int
    offset: int


class BeneficiarioDetalle(BaseModel):
    ID: int
    TIPO_DOCUMENTO: Optional[str] = None
    DOCUMENTO: Optional[str] = None
    NOMBRE1: Optional[str] = None
    NOMBRE2: Optional[str] = None
    APELLIDO1: Optional[str] = None
    APELLIDO2: Optional[str] = None
    FECHA_NACIMIENTO: Optional[str] = None
    SEXO: Optional[str] = None
    DIRECCION: Optional[str] = None
    CIUDAD: Optional[str] = None
    DEPARTAMENTO: Optional[str] = None
    CORREO: Optional[str] = None
    TELEFONO: Optional[str] = None
    FECHA_INGRESO: Optional[str] = None
    EMPRESA: Optional[str] = None
    ESTADO: Optional[str] = None


class BeneficiarioCrear(BaseModel):
    TIPO_DOCUMENTO: str
    DOCUMENTO: str
    NOMBRE1: str
    NOMBRE2: Optional[str] = None
    APELLIDO1: str
    APELLIDO2: Optional[str] = None
    FECHA_NACIMIENTO: date
    SEXO: Optional[str] = None
    DIRECCION: Optional[str] = None
    CIUDAD: str
    DEPARTAMENTO: str
    CORREO: Optional[str] = None
    TELEFONO: Optional[str] = None
    EMPRESA: Optional[str] = None
    EPS: Optional[str] = None
    OTRAEPS: Optional[str] = None
    PLAN_SALUD: Optional[str] = None
    PLAN_NOMBRE: Optional[str] = None


class CreacionBeneficiarioResultado(BaseModel):
    beneficiario: BeneficiarioDetalle
    usuario_servinte_creado: bool
    marcado_en_incle: bool


class BeneficiarioActivar(BaseModel):
    FECHA_INGRESO: date


class ActivacionBeneficiarioResultado(BaseModel):
    beneficiario: BeneficiarioDetalle
    registros_incle_desmarcados: int


class DesactivacionBeneficiarioResultado(BaseModel):
    beneficiario: BeneficiarioDetalle
    registros_incle_marcados: int


class BeneficiarioUpdate(BaseModel):
    TIPO_DOCUMENTO: Optional[str] = None
    DOCUMENTO: Optional[str] = None
    NOMBRE1: Optional[str] = None
    NOMBRE2: Optional[str] = None
    APELLIDO1: Optional[str] = None
    APELLIDO2: Optional[str] = None
    FECHA_NACIMIENTO: Optional[date] = None
    SEXO: Optional[str] = None
    DIRECCION: Optional[str] = None
    CIUDAD: Optional[str] = None
    DEPARTAMENTO: Optional[str] = None
    CORREO: Optional[str] = None
    TELEFONO: Optional[str] = None
    EMPRESA: Optional[str] = None
    ESTADO: Optional[str] = None