"""agregar autonumeracion (secuencia + trigger) a ids crm mercadeo

Revision ID: 4e379ceb9f70
Revises: 2cc3829900e2
Create Date: 2026-07-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4e379ceb9f70'
down_revision: Union[str, Sequence[str], None] = '2cc3829900e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tablas propias del CRM Mercadeo cuya columna id se creo con
# autoincrement=True (bandera solo de SQLAlchemy, sin efecto en Oracle) en
# lugar de generarse automaticamente en la base de datos. Se excluyen
# mercadeo_crm_campana_segmento y mercadeo_crm_contacto_etiqueta (no tienen
# columna id, usan llave compuesta) y las tablas externas
# intranet_usuarios / intranet_planliga.
#
# Oracle no permite convertir una columna ya existente en IDENTITY via
# ALTER TABLE ... MODIFY (ORA-30673: esa clausula solo sirve para modificar
# una columna que YA es identity). Para autonumerar columnas de tablas ya
# creadas se usa el patron clasico de secuencia + trigger BEFORE INSERT.
#
# Se usa exec_driver_sql (en lugar de op.execute) porque el cuerpo del
# trigger contiene ":NEW.id", y SQLAlchemy interpreta ":NEW" como un bind
# parameter si se pasa por op.execute/text(). exec_driver_sql envia el SQL
# tal cual al driver de Oracle, sin parsear los ":".
TABLES = [
    "mercadeo_crm_campanas",
    "mercadeo_crm_etiquetas",
    "mercadeo_crm_segmentos",
    "mercadeo_crm_embudos",
    "mercadeo_crm_empresas",
    "mercadeo_crm_contactos",
    "mercadeo_crm_etapas_embudo",
    "mercadeo_crm_oportunidades",
    "mercadeo_crm_bitacora",
    "mercadeo_crm_proveedores",
    "mercadeo_crm_servicios",
    "mercadeo_crm_actividad",
    "mercadeo_crm_titular_servicios",
    "mercadeo_crm_importaciones",
]


def _names(table: str) -> tuple[str, str]:
    short = table.replace("mercadeo_crm_", "", 1)
    return f"seq_{short}", f"trg_{short}_bi"


def _drop_if_exists(conn, kind: str, name: str, missing_error: int) -> None:
    conn.exec_driver_sql(
        f"""
        BEGIN
            EXECUTE IMMEDIATE 'DROP {kind} {name}';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -{missing_error} THEN
                    RAISE;
                END IF;
        END;
        """
    )


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    for table in TABLES:
        seq_name, trg_name = _names(table)

        # Idempotente: si un intento anterior dejo la secuencia o el
        # trigger creados (el DDL de Oracle no se revierte solo), se
        # eliminan primero para poder recrearlos sin error.
        _drop_if_exists(conn, "TRIGGER", trg_name, 4080)  # ORA-04080: trigger does not exist
        _drop_if_exists(conn, "SEQUENCE", seq_name, 2289)  # ORA-02289: sequence does not exist

        conn.exec_driver_sql(
            f"CREATE SEQUENCE {seq_name} START WITH 1 INCREMENT BY 1 NOCACHE"
        )
        conn.exec_driver_sql(
            f"""
            CREATE OR REPLACE TRIGGER {trg_name}
            BEFORE INSERT ON {table}
            FOR EACH ROW
            WHEN (NEW.id IS NULL)
            BEGIN
                SELECT {seq_name}.NEXTVAL INTO :NEW.id FROM dual;
            END;
            """
        )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    for table in TABLES:
        seq_name, trg_name = _names(table)
        _drop_if_exists(conn, "TRIGGER", trg_name, 4080)
        _drop_if_exists(conn, "SEQUENCE", seq_name, 2289)
