from datetime import date

from sqlalchemy import ColumnElement, String, case, cast, func, literal_column, select
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


def _nombre_plan() -> ColumnElement:
    """Nombre del servicio + su categoria (ej. 'Plan Liga - 6 Beneficiarios')."""
    return Servicio.nombre + case(
        (Servicio.categoria.isnot(None), literal_column("' - '") + Servicio.categoria),
        else_=literal_column("''"),
    )


class TitularesBeneficiariosRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def obtener_titular(self, id_titular: int) -> dict | None:
        stmt = select(
            PlanLiga.id.label("ID_TITULAR"),
            PlanLiga.documento.label("DOCUMENTO"),
            PlanLiga.tipo.label("TIPO_DOCUMENTO"),
            PlanLiga.nombre1.label("NOMBRE1"),
            PlanLiga.nombre2.label("NOMBRE2"),
            PlanLiga.apellido1.label("APELLIDO1"),
            PlanLiga.apellido2.label("APELLIDO2"),
            func.to_char(PlanLiga.fecha_nacimiento, "YYYY-MM-DD").label(
                "FECHA_NACIMIENTO"
            ),
            PlanLiga.sexo.label("SEXO"),
            PlanLiga.correo.label("CORREO"),
            PlanLiga.telefono.label("TELEFONO"),
            PlanLiga.direccion.label("DIRECCION"),
            PlanLiga.ciudad.label("CIUDAD"),
            PlanLiga.departamento.label("DEPARTAMENTO"),
            PlanLiga.tipo_plan.label("TIPO_PLAN"),
            PlanLiga.tipo_afiliado.label("TIPO_AFILIADO"),
            PlanLiga.empresa.label("EMPRESA"),
            PlanLiga.eps.label("EPS"),
            PlanLiga.otraeps.label("OTRAEPS"),
            PlanLiga.plan_salud.label("PLAN_SALUD"),
            PlanLiga.plan_nombre.label("PLAN_NOMBRE"),
            PlanLiga.estado.label("ESTADO"),
            func.to_char(PlanLiga.fecha_ingreso, "YYYY-MM-DD").label("FECHA_INGRESO"),
        ).where(PlanLiga.id == id_titular)

        fila = self.db.execute(stmt).mappings().first()
        return dict(fila) if fila is not None else None

    def listar_planes(self) -> list[Servicio]:
        stmt = select(Servicio).order_by(Servicio.nombre)
        return list(self.db.scalars(stmt))

    def listar_nombres_planes(self) -> list[str]:
        stmt = select(_nombre_plan()).order_by(Servicio.nombre, Servicio.categoria)
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

    def _construir_condiciones(
        self,
        estado: str | None = None,
        plan: str | None = None,
        sexo: str | None = None,
        edad: str | None = None,
    ) -> list[ColumnElement]:
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
                    func.lower(_nombre_plan()) == plan.lower(),
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

        return condiciones

    def contar_titulares(
        self,
        estado: str | None = None,
        plan: str | None = None,
        sexo: str | None = None,
        edad: str | None = None,
    ) -> int:
        condiciones = self._construir_condiciones(estado, plan, sexo, edad)

        stmt = (
            select(func.count(func.distinct(PlanLiga.id)))
            .select_from(PlanLiga)
            .join(TitularServicio, TitularServicio.planliga_id == PlanLiga.id)
            .join(Servicio, Servicio.id == TitularServicio.servicio_id)
            .where(*condiciones)
        )
        return self.db.scalar(stmt) or 0

    def listar_titulares(
        self,
        limit: int = 6,
        offset: int = 0,
        estado: str | None = None,
        plan: str | None = None,
        sexo: str | None = None,
        edad: str | None = None,
    ) -> list[dict]:
        condiciones = self._construir_condiciones(estado, plan, sexo, edad)

        conteo_beneficiarios = func.coalesce(
            select(func.count())
            .select_from(PlanLigaBeneficiario)
            .where(PlanLigaBeneficiario.planliga_id == PlanLiga.id)
            .scalar_subquery(),
            0,
        )
        cupo_plan = func.coalesce(Servicio.max_beneficiarios, 0) + func.coalesce(
            Servicio.beneficiarios_adicionales, 0
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
                func.listagg(_nombre_plan(), literal_column("' | '"))
                .within_group(Servicio.nombre, Servicio.categoria)
                .label("PLANES"),
                func.listagg(
                    cast(conteo_beneficiarios, String(50))
                    + literal_column("'/'")
                    + cast(cupo_plan, String(50)),
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
            .offset(offset)
            .limit(limit)
        )

        return [dict(row) for row in self.db.execute(stmt).mappings().all()]
