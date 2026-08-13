"""agregar servicio a oportunidades

Revision ID: 50de73c962ba
Revises: fa9c415ee2f8
Create Date: 2026-08-13 00:00:00.000000

servicio_id (FK a intranet_planliga_tipo_plan) no alcanza para el "servicio"
que ofrece el CRM Comercial en Oportunidades/Tablero (Tamizajes, Brigadas de
Salud, Capacitaciones, etc.): ese catalogo es especifico de Plan Liga y no
tiene filas para esas categorias. Se agrega esta columna de texto libre en
paralelo (servicio_id se deja como esta, sin usar por ahora) para no perder
el dato al conectar esas pantallas al backend real. Se llama "servicio_nombre"
(no "servicio") porque el modelo ya tiene un atributo Python "servicio" para
la relationship hacia PlanLigaTipoPlan via servicio_id.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50de73c962ba'
down_revision: Union[str, Sequence[str], None] = 'fa9c415ee2f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLA = "mercadeo_crm_oportunidades"


def _columna_existe(conn, table: str, columna: str) -> bool:
    stmt = sa.text(
        "SELECT 1 FROM user_tab_columns WHERE table_name = :tabla AND column_name = :columna"
    )
    return conn.execute(stmt, {"tabla": table.upper(), "columna": columna.upper()}).first() is not None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    if not _columna_existe(conn, TABLA, "servicio_nombre"):
        conn.exec_driver_sql(f"ALTER TABLE {TABLA} ADD (servicio_nombre VARCHAR2(150))")


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    conn.exec_driver_sql(f"ALTER TABLE {TABLA} DROP COLUMN servicio_nombre")
