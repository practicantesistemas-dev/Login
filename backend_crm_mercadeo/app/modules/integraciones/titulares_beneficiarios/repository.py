from datetime import date

from sqlalchemy import String, cast, func, literal_column, select
from sqlalchemy.orm import Session

from app.models import PlanLiga, PlanLigaBeneficiario, Servicio, TitularServicio

ESTADO_ACTIVO = "A"
ESTADO_INACTIVO = "I"
ESTADOS_FILTRO = {"activo": ESTADO_ACTIVO, "inactivo": ESTADO_INACTIVO}

RANGOS_EDAD: dict[str, tuple[int, int | None]] = {
    "0-17": (0, 17),
    "18-35": (18, 35),
    "36-50": (36, 50),
    "51+": (51, None),
}


def _rango_fecha_nacimiento(edad: str, hoy: date) -> tuple[date | None, date | None]:
    edad_min, edad_max = RANGOS_EDAD[edad]
    fecha_nacimiento_max = hoy.replace(year=hoy.year - edad_min)
    fecha_nacimiento_min = (
        hoy.replace(year=hoy.year - edad_max - 1) if edad_max is not None else None
    )
    return fecha_nacimiento_min, fecha_nacimiento_max


class TitularesBeneficiariosRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar_planes(self) -> list[Servicio]:
        stmt = select(Servicio).order_by(Servicio.nombre)
        return list(self.db.scalars(stmt))

    def listar_nombres_planes(self) -> list[str]:
        stmt = select(Servicio.nombre).order_by(Servicio.nombre)
        return list(self.db.scalars(stmt))

    def contar_titulares_activos(self) -> int:
        stmt = select(func.count()).select_from(PlanLiga).where(
            PlanLiga.estado == ESTADO_ACTIVO
        )
        return self.db.scalar(stmt) or 0

    def contar_beneficiarios_activos(self) -> int:
        stmt = select(func.count()).select_from(PlanLigaBeneficiario).where(
            PlanLigaBeneficiario.estado == ESTADO_ACTIVO
        )
        return self.db.scalar(stmt) or 0

    def listar_titulares(
        self,
        limit: int = 6,
        estado: str | None = None,
        plan: str | None = None,
        sexo: str | None = None,
        edad: str | None = None,
    ) -> list[dict]:
        condiciones = []

        if estado:
            codigo = ESTADOS_FILTRO.get(estado.lower())
            if codigo:
                condiciones.append(PlanLiga.estado == codigo)

        if plan:
            condiciones.append(
                select(TitularServicio.id)
                .join(Servicio, Servicio.id == TitularServicio.servicio_id)
                .where(
                    TitularServicio.planliga_id == PlanLiga.id,
                    func.lower(Servicio.nombre) == plan.lower(),
                )
                .exists()
            )

        if sexo:
            condiciones.append(func.upper(PlanLiga.sexo) == sexo.upper())

        if edad:
            fecha_min, fecha_max = _rango_fecha_nacimiento(edad, date.today())
            condiciones.append(PlanLiga.fecha_nacimiento <= fecha_max)
            if fecha_min is not None:
                condiciones.append(PlanLiga.fecha_nacimiento > fecha_min)

        conteo_beneficiarios = func.coalesce(
            select(func.count())
            .select_from(PlanLigaBeneficiario)
            .where(PlanLigaBeneficiario.planliga_id == PlanLiga.id)
            .scalar_subquery(),
            0,
        )

        stmt = (
            select(
                PlanLiga.id.label("ID_TITULAR"),
                func.trim(
                    PlanLiga.nombre1
                    + literal_column("' '")
                    + func.coalesce(PlanLiga.nombre2, "")
                    + literal_column("' '")
                    + func.coalesce(PlanLiga.apellido1, "")
                    + literal_column("' '")
                    + func.coalesce(PlanLiga.apellido2, "")
                ).label("TITULAR"),
                PlanLiga.documento.label("DOCUMENTO"),
                PlanLiga.tipo.label("TIPO_DOCUMENTO"),
                PlanLiga.empresa.label("EMPRESA"),
                func.listagg(Servicio.nombre, literal_column("' | '"))
                .within_group(Servicio.nombre)
                .label("PLANES"),
                func.listagg(
                    cast(conteo_beneficiarios, String(50))
                    + literal_column("'/'")
                    + cast(Servicio.max_beneficiarios, String(50)),
                    literal_column("' | '"),
                )
                .within_group(Servicio.nombre)
                .label("BENEFICIARIOS"),
                PlanLiga.correo.label("EMAIL"),
                PlanLiga.telefono.label("TELEFONO"),
                func.to_char(PlanLiga.fecha_ingreso, "YYYY-MM-DD").label("INSCRIPCION"),
                PlanLiga.estado.label("ESTADO"),
            )
            .select_from(PlanLiga)
            .join(TitularServicio, TitularServicio.planliga_id == PlanLiga.id)
            .join(Servicio, Servicio.id == TitularServicio.servicio_id)
            .where(*condiciones)
            .group_by(
                PlanLiga.id,
                PlanLiga.nombre1,
                PlanLiga.nombre2,
                PlanLiga.apellido1,
                PlanLiga.apellido2,
                PlanLiga.documento,
                PlanLiga.tipo,
                PlanLiga.empresa,
                PlanLiga.correo,
                PlanLiga.telefono,
                PlanLiga.fecha_ingreso,
                PlanLiga.estado,
            )
            .order_by(PlanLiga.fecha_ingreso.desc())
            .limit(limit)
        )

        return [dict(row) for row in self.db.execute(stmt).mappings().all()]
