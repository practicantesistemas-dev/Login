"""renombrar ciudad a municipio y agregar departamento en contactos

Revision ID: fa9c415ee2f8
Revises: ea47fe96f819
Create Date: 2026-08-05 21:00:00.000000

El modelo (app/models.py) espera mercadeo_crm_contactos.municipio y
mercadeo_crm_contactos.departamento, pero la tabla nunca paso por una
migracion que hiciera ese cambio: la creacion original solo definio
"ciudad". Esta migracion:
  - renombra ciudad -> municipio si la tabla todavia no paso por el
    rename manual (entornos nuevos creados desde cero con Alembic)
  - agrega departamento si todavia no existe (entornos donde ya se
    aplico el rename manual, para no fallar por columna duplicada)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa9c415ee2f8'
down_revision: Union[str, Sequence[str], None] = 'ea47fe96f819'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLA = "mercadeo_crm_contactos"


def _columna_existe(conn, table: str, columna: str) -> bool:
    stmt = sa.text(
        "SELECT 1 FROM user_tab_columns WHERE table_name = :tabla AND column_name = :columna"
    )
    return conn.execute(stmt, {"tabla": table.upper(), "columna": columna.upper()}).first() is not None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    if _columna_existe(conn, TABLA, "ciudad") and not _columna_existe(conn, TABLA, "municipio"):
        conn.exec_driver_sql(f"ALTER TABLE {TABLA} RENAME COLUMN ciudad TO municipio")

    if not _columna_existe(conn, TABLA, "departamento"):
        conn.exec_driver_sql(f"ALTER TABLE {TABLA} ADD (departamento VARCHAR2(2))")


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    conn.exec_driver_sql(f"ALTER TABLE {TABLA} DROP COLUMN departamento")
    conn.exec_driver_sql(f"ALTER TABLE {TABLA} RENAME COLUMN municipio TO ciudad")
