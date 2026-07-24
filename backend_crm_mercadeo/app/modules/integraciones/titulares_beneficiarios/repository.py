from datetime import date, datetime

from sqlalchemy import (
    ColumnElement,
    String,
    case,
    cast,
    func,
    literal_column,
    or_,
    select,
    update,
)
from sqlalchemy.orm import Session

from app.models import PlanLiga, PlanLigaBeneficiario, PlanLigaTipoPlan

ESTADO_ACTIVO = "A"
ESTADO_INACTIVO = "I"
ESTADOS_FILTRO = {"activo": ESTADO_ACTIVO, "inactivo": ESTADO_INACTIVO}

# El Plan Estandar (base implicita, sin fila propia en el catalogo) es de 4
# beneficiarios + 1 titular. Cuando un tipo_plan tiene beneficiarios_adicionales
# (> 0), esos adicionales se suman sobre esa base fija, no sobre la columna
# BENEFICIARIOS de esa fila (que en los planes "X Adicional" no representa el
# cupo total, sino solo el incremento). Si no tiene adicionales, el cupo es
# directamente el valor de BENEFICIARIOS de ese tipo_plan.
BENEFICIARIOS_PLAN_ESTANDAR = 4

RANGOS_EDAD: dict[str, tuple[int, int | None]] = {
    "0-17": (0, 17),
    "18-35": (18, 35),
    "36-50": (36, 50),
    "51+": (51, None),
}

# Solo los campos de interes para Mercadeo son editables por API; los legacy
# de plan (tipo_plan, eps, plan_nombre, etc.) y los de sistema/auditoria
# quedan afuera a proposito (ver conversacion sobre columnas expuestas).
CAMPOS_TITULAR_EDITABLES = {
    "DOCUMENTO": "documento",
    "TIPO_DOCUMENTO": "tipo",
    "NOMBRE1": "nombre1",
    "NOMBRE2": "nombre2",
    "APELLIDO1": "apellido1",
    "APELLIDO2": "apellido2",
    "FECHA_NACIMIENTO": "fecha_nacimiento",
    "SEXO": "sexo",
    "CORREO": "correo",
    "TELEFONO": "telefono",
    "DIRECCION": "direccion",
    "CIUDAD": "ciudad",
    "DEPARTAMENTO": "departamento",
    "EMPRESA": "empresa",
    "ESTADO": "estado",
}

CAMPOS_TITULAR_CREACION = {
    "TIPO_PLAN": "tipo_plan",
    "TIPO_PLAN_ID": "tipo_plan_id",
    "TIPO_DOCUMENTO": "tipo",
    "DOCUMENTO": "documento",
    "NOMBRE1": "nombre1",
    "NOMBRE2": "nombre2",
    "APELLIDO1": "apellido1",
    "APELLIDO2": "apellido2",
    "FECHA_NACIMIENTO": "fecha_nacimiento",
    "SEXO": "sexo",
    "DIRECCION": "direccion",
    "CIUDAD": "ciudad",
    "DEPARTAMENTO": "departamento",
    "CORREO": "correo",
    "TELEFONO": "telefono",
    "TIPO_AFILIADO": "tipo_afiliado",
    "EMPRESA": "empresa",
    "EPS": "eps",
    "OTRAEPS": "otraeps",
    "PLAN_SALUD": "plan_salud",
    "PLAN_NOMBRE": "plan_nombre",
}

CAMPOS_BENEFICIARIO_CREACION = {
    "TIPO_DOCUMENTO": "tipo",
    "DOCUMENTO": "documento",
    "NOMBRE1": "nombre1",
    "NOMBRE2": "nombre2",
    "APELLIDO1": "apellido1",
    "APELLIDO2": "apellido2",
    "FECHA_NACIMIENTO": "fecha_nacimiento",
    "SEXO": "sexo",
    "DIRECCION": "direccion",
    "CIUDAD": "ciudad",
    "DEPARTAMENTO": "departamento",
    "CORREO": "correo",
    "TELEFONO": "telefono",
    "EMPRESA": "empresa",
    "EPS": "eps",
    "OTRAEPS": "otraeps",
    "PLAN_SALUD": "plan_salud",
    "PLAN_NOMBRE": "plan_nombre",
}

CAMPOS_BENEFICIARIO_EDITABLES = {
    "TIPO_DOCUMENTO": "tipo",
    "DOCUMENTO": "documento",
    "NOMBRE1": "nombre1",
    "NOMBRE2": "nombre2",
    "APELLIDO1": "apellido1",
    "APELLIDO2": "apellido2",
    "FECHA_NACIMIENTO": "fecha_nacimiento",
    "SEXO": "sexo",
    "DIRECCION": "direccion",
    "CIUDAD": "ciudad",
    "DEPARTAMENTO": "departamento",
    "CORREO": "correo",
    "TELEFONO": "telefono",
    "EMPRESA": "empresa",
    "ESTADO": "estado",
}


def _rango_fecha_nacimiento(edad: str, hoy: date) -> tuple[date | None, date | None]:
    edad_min, edad_max = RANGOS_EDAD[edad]
    fecha_nacimiento_max = hoy.replace(year=hoy.year - edad_min)
    fecha_nacimiento_min = (
        hoy.replace(year=hoy.year - edad_max - 1) if edad_max is not None else None
    )
    return fecha_nacimiento_min, fecha_nacimiento_max


def _nombre_plan() -> ColumnElement:
    """Nombre del tipo de plan + su categoria (ej. 'Plan Liga - 6 Beneficiarios')."""
    return PlanLigaTipoPlan.nombre + case(
        (
            PlanLigaTipoPlan.categoria.isnot(None),
            literal_column("' - '") + PlanLigaTipoPlan.categoria,
        ),
        else_=literal_column("''"),
    )


def _cupo_plan() -> ColumnElement:
    """Cupo total de beneficiarios del tipo_plan (ver BENEFICIARIOS_PLAN_ESTANDAR)."""
    return case(
        (
            PlanLigaTipoPlan.beneficiarios_adicionales > 0,
            BENEFICIARIOS_PLAN_ESTANDAR + PlanLigaTipoPlan.beneficiarios_adicionales,
        ),
        else_=func.coalesce(PlanLigaTipoPlan.beneficiarios, 0),
    )


def _columnas_beneficiario() -> list[ColumnElement]:
    return [
        PlanLigaBeneficiario.id.label("ID"),
        PlanLigaBeneficiario.tipo.label("TIPO_DOCUMENTO"),
        PlanLigaBeneficiario.documento.label("DOCUMENTO"),
        PlanLigaBeneficiario.nombre1.label("NOMBRE1"),
        PlanLigaBeneficiario.nombre2.label("NOMBRE2"),
        PlanLigaBeneficiario.apellido1.label("APELLIDO1"),
        PlanLigaBeneficiario.apellido2.label("APELLIDO2"),
        func.to_char(PlanLigaBeneficiario.fecha_nacimiento, "YYYY-MM-DD").label(
            "FECHA_NACIMIENTO"
        ),
        PlanLigaBeneficiario.sexo.label("SEXO"),
        PlanLigaBeneficiario.direccion.label("DIRECCION"),
        PlanLigaBeneficiario.ciudad.label("CIUDAD"),
        PlanLigaBeneficiario.departamento.label("DEPARTAMENTO"),
        PlanLigaBeneficiario.correo.label("CORREO"),
        PlanLigaBeneficiario.telefono.label("TELEFONO"),
        func.to_char(PlanLigaBeneficiario.fecha_ingreso, "DD/MM/YYYY").label(
            "FECHA_INGRESO"
        ),
        PlanLigaBeneficiario.empresa.label("EMPRESA"),
        PlanLigaBeneficiario.estado.label("ESTADO"),
    ]


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
            func.to_char(PlanLiga.fecha_nacimiento, "DD/MM/YYYY").label(
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
            func.to_char(PlanLiga.fecha_ingreso, "DD/MM/YYYY").label("FECHA_INGRESO"),
        ).where(PlanLiga.id == id_titular)

        fila = self.db.execute(stmt).mappings().first()
        return dict(fila) if fila is not None else None

    def obtener_fecha_ingreso_titular(self, id_titular: int) -> date | None:
        titular = self.db.get(PlanLiga, id_titular)
        return titular.fecha_ingreso if titular else None

    def listar_beneficiarios(self, id_titular: int) -> list[dict]:
        stmt = (
            select(*_columnas_beneficiario())
            .where(PlanLigaBeneficiario.planliga_id == id_titular)
            .order_by(PlanLigaBeneficiario.orden, PlanLigaBeneficiario.id)
        )

        return [dict(row) for row in self.db.execute(stmt).mappings().all()]

    def obtener_beneficiario(self, id_titular: int, id_beneficiario: int) -> dict | None:
        stmt = select(*_columnas_beneficiario()).where(
            PlanLigaBeneficiario.id == id_beneficiario,
            PlanLigaBeneficiario.planliga_id == id_titular,
        )

        fila = self.db.execute(stmt).mappings().first()
        return dict(fila) if fila is not None else None

    def listar_planes(self) -> list[PlanLigaTipoPlan]:
        stmt = select(PlanLigaTipoPlan).order_by(PlanLigaTipoPlan.nombre)
        return list(self.db.scalars(stmt))

    def listar_nombres_planes(self) -> list[dict]:
        stmt = (
            select(PlanLigaTipoPlan.id.label("ID"), _nombre_plan().label("NOMBRE"))
            .order_by(PlanLigaTipoPlan.nombre, PlanLigaTipoPlan.categoria)
        )
        return [dict(row) for row in self.db.execute(stmt).mappings().all()]

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
        tipo_plan_id: int | None = None,
        sexo: str | None = None,
        edad: str | None = None,
        busqueda: str | None = None,
    ) -> list[ColumnElement]:
        estado = None if estado and estado.strip().lower() == "todos" else estado
        sexo = None if sexo and sexo.strip().lower() == "todos" else sexo
        edad = None if edad and edad.strip().lower() == "todos" else edad

        condiciones = []

        if estado:
            codigo = ESTADOS_FILTRO.get(estado.lower())
            if codigo:
                condiciones.append(PlanLiga.estado == codigo)

        if tipo_plan_id:
            condiciones.append(PlanLiga.tipo_plan_id == tipo_plan_id)

        if sexo:
            condiciones.append(func.upper(PlanLiga.sexo) == sexo.upper())

        if edad:
            fecha_min, fecha_max = _rango_fecha_nacimiento(edad, date.today())
            condiciones.append(PlanLiga.fecha_nacimiento <= fecha_max)
            if fecha_min is not None:
                condiciones.append(PlanLiga.fecha_nacimiento > fecha_min)

        if busqueda and busqueda.strip():
            termino = f"%{busqueda.strip().upper()}%"
            nombre_completo = (
                func.coalesce(PlanLiga.nombre1, "")
                + literal_column("' '")
                + func.coalesce(PlanLiga.nombre2, "")
                + literal_column("' '")
                + func.coalesce(PlanLiga.apellido1, "")
                + literal_column("' '")
                + func.coalesce(PlanLiga.apellido2, "")
            )
            condiciones.append(
                or_(
                    func.upper(nombre_completo).like(termino),
                    func.upper(func.coalesce(PlanLiga.documento, "")).like(termino),
                    func.upper(func.coalesce(PlanLiga.empresa, "")).like(termino),
                    func.upper(func.coalesce(PlanLiga.correo, "")).like(termino),
                )
            )

        return condiciones

    def contar_titulares(
        self,
        estado: str | None = None,
        tipo_plan_id: int | None = None,
        sexo: str | None = None,
        edad: str | None = None,
        busqueda: str | None = None,
    ) -> int:
        condiciones = self._construir_condiciones(estado, tipo_plan_id, sexo, edad, busqueda)

        stmt = select(func.count()).select_from(PlanLiga).where(*condiciones)
        return self.db.scalar(stmt) or 0

    def listar_titulares(
        self,
        limit: int = 6,
        offset: int = 0,
        estado: str | None = None,
        tipo_plan_id: int | None = None,
        sexo: str | None = None,
        edad: str | None = None,
        busqueda: str | None = None,
    ) -> list[dict]:
        condiciones = self._construir_condiciones(estado, tipo_plan_id, sexo, edad, busqueda)

        conteo_beneficiarios = func.coalesce(
            select(func.count())
            .select_from(PlanLigaBeneficiario)
            .where(PlanLigaBeneficiario.planliga_id == PlanLiga.id)
            .scalar_subquery(),
            0,
        )
        cupo_plan = _cupo_plan()

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
                _nombre_plan().label("PLANES"),
                (
                    cast(conteo_beneficiarios, String(50))
                    + literal_column("'/'")
                    + cast(cupo_plan, String(50))
                ).label("BENEFICIARIOS"),
                PlanLiga.correo.label("EMAIL"),
                PlanLiga.telefono.label("TELEFONO"),
                func.to_char(PlanLiga.fecha_ingreso, "DD/MM/YYYY").label("INSCRIPCION"),
                PlanLiga.estado.label("ESTADO"),
            )
            .select_from(PlanLiga)
            .outerjoin(PlanLigaTipoPlan, PlanLigaTipoPlan.id == PlanLiga.tipo_plan_id)
            .where(*condiciones)
            .order_by(PlanLiga.fecha_ingreso.desc())
            .offset(offset)
            .limit(limit)
        )

        return [dict(row) for row in self.db.execute(stmt).mappings().all()]

    def actualizar_titular(self, id_titular: int, datos: dict) -> bool:
        titular = self.db.get(PlanLiga, id_titular)
        if titular is None:
            return False
        for campo, valor in datos.items():
            atributo = CAMPOS_TITULAR_EDITABLES.get(campo)
            if atributo:
                setattr(titular, atributo, valor)
        self.db.commit()
        return True

    def actualizar_beneficiario(
        self, id_titular: int, id_beneficiario: int, datos: dict
    ) -> bool:
        beneficiario = self.db.get(PlanLigaBeneficiario, id_beneficiario)
        if beneficiario is None or beneficiario.planliga_id != id_titular:
            return False
        for campo, valor in datos.items():
            atributo = CAMPOS_BENEFICIARIO_EDITABLES.get(campo)
            if atributo:
                setattr(beneficiario, atributo, valor)
        self.db.commit()
        return True

    def existe_documento(self, tipo: str, documento: str) -> str | None:
        """Retorna 'TITULAR', 'BENEFICIARIO' o None si el documento no esta registrado."""
        if (
            self.db.scalar(
                select(PlanLiga.id)
                .where(PlanLiga.tipo == tipo, PlanLiga.documento == documento)
                .limit(1)
            )
            is not None
        ):
            return "TITULAR"

        if (
            self.db.scalar(
                select(PlanLigaBeneficiario.id)
                .where(
                    PlanLigaBeneficiario.tipo == tipo,
                    PlanLigaBeneficiario.documento == documento,
                )
                .limit(1)
            )
            is not None
        ):
            return "BENEFICIARIO"

        return None

    def crear_titular(self, datos: dict, fecha_ingreso: date) -> int:
        campos = {
            atributo: datos.get(campo)
            for campo, atributo in CAMPOS_TITULAR_CREACION.items()
        }
        titular = PlanLiga(
            **campos,
            estado=ESTADO_ACTIVO,
            fecha_ingreso=fecha_ingreso,
            fecha_registro=datetime.now(),
        )
        self.db.add(titular)
        self.db.commit()
        self.db.refresh(titular)
        return titular.id

    def contar_beneficiarios(self, id_titular: int) -> int:
        stmt = select(func.count()).select_from(PlanLigaBeneficiario).where(
            PlanLigaBeneficiario.planliga_id == id_titular
        )
        return self.db.scalar(stmt) or 0

    def cupo_beneficiarios_titular(self, id_titular: int) -> int:
        stmt = (
            select(_cupo_plan())
            .select_from(PlanLiga)
            .join(PlanLigaTipoPlan, PlanLigaTipoPlan.id == PlanLiga.tipo_plan_id)
            .where(PlanLiga.id == id_titular)
        )
        return self.db.scalar(stmt) or 0

    def crear_beneficiario(
        self,
        id_titular: int,
        datos: dict,
        fecha_ingreso: date,
        orden: int,
        tipo_plan: str | None,
    ) -> int:
        campos = {
            atributo: datos.get(campo)
            for campo, atributo in CAMPOS_BENEFICIARIO_CREACION.items()
        }
        beneficiario = PlanLigaBeneficiario(
            **campos,
            planliga_id=id_titular,
            tipo_plan=tipo_plan,
            orden=orden,
            estado=ESTADO_ACTIVO,
            tipo_afiliado="2",
            fecha_ingreso=fecha_ingreso,
            fecha_registro=datetime.now(),
        )
        self.db.add(beneficiario)
        self.db.commit()
        self.db.refresh(beneficiario)
        return beneficiario.id

    def activar_beneficiario(
        self, id_titular: int, id_beneficiario: int, fecha_ingreso: date
    ) -> bool:
        beneficiario = self.db.get(PlanLigaBeneficiario, id_beneficiario)
        if beneficiario is None or beneficiario.planliga_id != id_titular:
            return False
        beneficiario.estado = ESTADO_ACTIVO
        beneficiario.fecha_ingreso = fecha_ingreso
        self.db.commit()
        return True

    def desactivar_beneficiario(self, id_titular: int, id_beneficiario: int) -> bool:
        beneficiario = self.db.get(PlanLigaBeneficiario, id_beneficiario)
        if beneficiario is None or beneficiario.planliga_id != id_titular:
            return False
        beneficiario.estado = ESTADO_INACTIVO
        self.db.commit()
        return True

    def activar_titular(self, id_titular: int, fecha_ingreso: date) -> bool:
        titular = self.db.get(PlanLiga, id_titular)
        if titular is None:
            return False
        titular.estado = ESTADO_ACTIVO
        titular.fecha_ingreso = fecha_ingreso
        # titular.renovado = "S"  # TODO: descomentar en produccion (columna aun no existe en BD de pruebas)
        self.db.commit()
        return True

    def activar_beneficiarios(self, id_titular: int, fecha_ingreso: date) -> int:
        stmt = (
            update(PlanLigaBeneficiario)
            .where(PlanLigaBeneficiario.planliga_id == id_titular)
            .values(
                estado=ESTADO_ACTIVO,
                fecha_ingreso=fecha_ingreso,
                # renovado="S",  # TODO: descomentar en produccion (columna aun no existe en BD de pruebas)
            )
        )
        resultado = self.db.execute(stmt)
        self.db.commit()
        return resultado.rowcount

    def desactivar_titular(self, id_titular: int) -> bool:
        titular = self.db.get(PlanLiga, id_titular)
        if titular is None:
            return False
        titular.estado = ESTADO_INACTIVO
        self.db.commit()
        return True

    def desactivar_beneficiarios(self, id_titular: int) -> list[tuple[str, str]]:
        stmt_select = select(
            PlanLigaBeneficiario.tipo, PlanLigaBeneficiario.documento
        ).where(
            PlanLigaBeneficiario.planliga_id == id_titular,
            PlanLigaBeneficiario.estado == ESTADO_ACTIVO,
        )
        beneficiarios = [tuple(fila) for fila in self.db.execute(stmt_select).all()]

        stmt_update = (
            update(PlanLigaBeneficiario)
            .where(
                PlanLigaBeneficiario.planliga_id == id_titular,
                PlanLigaBeneficiario.estado == ESTADO_ACTIVO,
            )
            .values(estado=ESTADO_INACTIVO)
        )
        self.db.execute(stmt_update)
        self.db.commit()
        return beneficiarios
