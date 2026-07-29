from pydantic import BaseModel


class DepartamentoItem(BaseModel):
    CODIGO: str
    NOMBRE: str


class MunicipioItem(BaseModel):
    CODIGO: str
    NOMBRE: str
    DEPARTAMENTO_CODIGO: str
    DEPARTAMENTO_NOMBRE: str
