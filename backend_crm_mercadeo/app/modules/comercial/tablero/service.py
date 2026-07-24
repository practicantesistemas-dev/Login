from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Contacto
from app.modules.comercial.tablero.repository import TableroRepository
from app.modules.comercial.tablero.schemas import (
    ActividadRecienteItem,
    DistribucionContactos,
    EtapaEmbudoItem,
    IndicadorItem,
    KpiItem,
    Periodo,
    ResumenDashboard,
    TopPlanItem,
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
                usuario_nombre=usuario.nombres if usuario else None,
            )
            for bitacora, contacto, empresa, usuario in filas
        ]

    def distribucion_contactos(self, periodo: Periodo = "30d") -> DistribucionContactos:
        ahora = datetime.now(timezone.utc)
        desde = _inicio_periodo(periodo, ahora)

        r = self.repository
        total = r.contar_total_contactos(desde, ahora)

        def item(cantidad: int) -> IndicadorItem:
            porcentaje = round(cantidad / total * 100, 1) if total else 0.0
            return IndicadorItem(cantidad=cantidad, porcentaje=porcentaje)

        return DistribucionContactos(
            total=total,
            clientes_activos=item(r.contar_clientes_activos(desde, ahora)),
            prospectos_activos=item(r.contar_prospectos_activos(desde, ahora)),
            inactivos=item(r.contar_contactos_inactivos(desde, ahora)),
        )

    def embudo_comercial(
        self, embudo_id: int | None = None, periodo: Periodo = "30d"
    ) -> list[EtapaEmbudoItem]:
        ahora = datetime.now(timezone.utc)
        desde = _inicio_periodo(periodo, ahora)

        filas = self.repository.embudo_comercial(embudo_id, desde, ahora)
        return [
            EtapaEmbudoItem(
                etapa_id=etapa.id,
                embudo_id=etapa.embudo_id,
                nombre=etapa.nombre,
                orden=etapa.orden,
                cantidad=cantidad,
            )
            for etapa, cantidad in filas
        ]

    def top_planes(self, limit: int = 4) -> list[TopPlanItem]:
        filas = self.repository.top_planes(limit)
        total = sum(fila.total for fila in filas)
        return [
            TopPlanItem(
                plan_id=fila.plan_id,
                nombre=fila.nombre,
                solicitudes=fila.total,
                porcentaje=round(fila.total / total * 100, 1) if total else 0.0,
            )
            for fila in filas
        ]
