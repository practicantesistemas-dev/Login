from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Periodo = Literal["7d", "30d", "trimestre", "anio", "todo"]


class KpiItem(BaseModel):
    valor: int


class ResumenDashboard(BaseModel):
    contactos: KpiItem
    titulares_pl: KpiItem
    empresas: KpiItem
    oportunidades: KpiItem
    servicios: KpiItem
    seguimientos: KpiItem


class ActividadRecienteItem(BaseModel):
    id: int
    tipo: str | None = None
    descripcion: str | None = None
    proximo_paso: str | None = None
    fecha: datetime | None = None
    contacto_id: int | None = None
    contacto_nombre: str | None = None
    empresa_id: int | None = None
    empresa_nombre: str | None = None
    usuario_id: int | None = None
    usuario_nombre: str | None = None


class TopServicioItem(BaseModel):
    servicio_id: int
    nombre: str
    solicitudes: int
    porcentaje: float


class IndicadorItem(BaseModel):
    cantidad: int
    porcentaje: float


class DistribucionContactos(BaseModel):
    total: int
    clientes_activos: IndicadorItem
    prospectos_activos: IndicadorItem
    inactivos: IndicadorItem


class EtapaEmbudoItem(BaseModel):
    etapa_id: int
    embudo_id: int | None = None
    nombre: str
    orden: int | None = None
    cantidad: int
