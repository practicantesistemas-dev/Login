from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Contacto
from app.modules.comercial.tablero.repository import TableroRepository
from app.modules.comercial.tablero.schemas import (
    ActividadRecienteItem,
    DistribucionContactosItem,
    KpiItem,
    Periodo,
    ResumenDashboard,
    TopServicioItem,
)


def _inicio_periodo(periodo: Periodo, ahora: datetime) -> datetime | None:
    if periodo == "7d":
        return ahora - timedelta(days=7)
    if periodo == "30d":
        return ahora - timedelta(days=30)
    if periodo == "trimestre":
        mes_inicio = ((ahora.month - 1) // 3) * 3 + 1
        return ahora.replace(month=mes_inicio, day=1, hour=0, minute=0, second=0, microsecond=0)
    if periodo == "anio":
        return ahora.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return None  # "todo": sin limite inferior


def _nombre_contacto(contacto: Contacto | None) -> str | None:
    if contacto is None:
        return None
    partes = [contacto.nombre1, contacto.apellido1]
    return " ".join(parte for parte in partes if parte)


class TableroService:
    def __init__(self, db: Session) -> None:
        self.repository = TableroRepository(db)

    def resumen(self, periodo: Periodo = "30d") -> ResumenDashboard:
        ahora = datetime.now(timezone.utc)
        desde = _inicio_periodo(periodo, ahora)

        r = self.repository
        return ResumenDashboard(
            contactos=KpiItem(valor=r.contar_contactos(desde, ahora)),
            titulares_pl=KpiItem(valor=r.contar_titulares_pl_activos(desde, ahora)),
            empresas=KpiItem(valor=r.contar_empresas_vinculadas(desde, ahora)),
            oportunidades=KpiItem(valor=r.contar_oportunidades_en_curso(desde, ahora)),
            servicios=KpiItem(valor=r.contar_servicios_plan_liga_activos(desde, ahora)),
            seguimientos=KpiItem(valor=r.contar_seguimientos_pendientes(desde, ahora)),
        )

    def actividad_reciente(self, limit: int = 10) -> list[ActividadRecienteItem]:
        filas = self.repository.actividad_reciente(limit)
        return [
            ActividadRecienteItem(
                id=bitacora.id,
                tipo=bitacora.tipo,
                descripcion=bitacora.descripcion,
                proximo_paso=bitacora.proximo_paso,
                fecha=bitacora.fecha,
                contacto_id=bitacora.contacto_id,
                contacto_nombre=_nombre_contacto(contacto),
                empresa_id=bitacora.empresa_id,
                empresa_nombre=empresa.razon_social if empresa else None,
                usuario_id=bitacora.usuario_id,
            )
            for bitacora, contacto, empresa in filas
        ]

    def distribucion_contactos(self) -> list[DistribucionContactosItem]:
        filas = self.repository.distribucion_contactos()
        total = sum(cantidad for _, cantidad in filas)
        return [
            DistribucionContactosItem(
                estado=estado or "Sin estado",
                cantidad=cantidad,
                porcentaje=round(cantidad / total * 100, 1) if total else 0.0,
            )
            for estado, cantidad in filas
        ]

    def top_servicios(self, limit: int = 4) -> list[TopServicioItem]:
        filas = self.repository.top_servicios(limit)
        total = sum(cantidad for _, cantidad in filas)
        return [
            TopServicioItem(
                servicio_id=servicio.id,
                nombre=servicio.nombre,
                solicitudes=cantidad,
                porcentaje=round(cantidad / total * 100, 1) if total else 0.0,
            )
            for servicio, cantidad in filas
        ]
