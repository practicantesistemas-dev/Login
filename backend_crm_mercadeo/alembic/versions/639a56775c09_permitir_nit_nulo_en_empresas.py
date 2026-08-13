"""permitir nit nulo en empresas

Revision ID: 639a56775c09
Revises: 50de73c962ba
Create Date: 2026-08-13 00:00:00.000000

Las empresas que se importan desde intranet_planliga.empresa (nombre libre que cada
titular escribe, sin NIT asociado) no tienen forma de traer un NIT real. nit sigue
siendo UNIQUE (Oracle permite varios NULL en una columna UNIQUE), solo deja de ser
obligatorio.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '639a56775c09'
down_revision: Union[str, Sequence[str], None] = '50de73c962ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLA = "mercadeo_crm_empresas"


def _es_nullable(conn, table: str, columna: str) -> bool | None:
    stmt = sa.text(
        "SELECT nullable FROM user_tab_columns WHERE table_name = :tabla AND column_name = :columna"
    )
    fila = conn.execute(stmt, {"tabla": table.upper(), "columna": columna.upper()}).first()
    return None if fila is None else fila[0] == "Y"


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    if _es_nullable(conn, TABLA, "nit") is False:
        conn.exec_driver_sql(f"ALTER TABLE {TABLA} MODIFY (nit NULL)")


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    conn.exec_driver_sql(f"ALTER TABLE {TABLA} MODIFY (nit NOT NULL)")
