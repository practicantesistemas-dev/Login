"""convertir nombre_empresa de bitacora a texto libre

Revision ID: ea47fe96f819
Revises: c128fff4a64a
Create Date: 2026-07-28 08:49:30.182912

En produccion la columna empresa_id de mercadeo_crm_bitacora ya fue
renombrada a nombre_empresa (fuera de Alembic) pero sigue siendo NUMBER
con FK a mercadeo_crm_empresas. Se decide que a partir de ahora sea texto
libre (nombre escrito a mano), sin depender de un registro formal en
mercadeo_crm_empresas. Esta migracion:
  - localiza y elimina la FK (sin nombre fijo: Oracle la genero con un
    nombre SYS_ automatico al no haberse nombrado en la creacion original)
  - renombra empresa_id -> nombre_empresa si la tabla todavia no paso por
    el rename manual (entornos nuevos creados desde cero con Alembic)
  - cambia el tipo de columna a VARCHAR2(200)

Solo funciona si la columna esta vacia (NULL en todas las filas), que es
el caso tanto en produccion como en cualquier entorno nuevo.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea47fe96f819'
down_revision: Union[str, Sequence[str], None] = 'c128fff4a64a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLA = "mercadeo_crm_bitacora"


def _fk_constraint_name(conn, table: str, columnas: tuple[str, ...]) -> str | None:
    stmt = sa.text(
        """
        SELECT a.constraint_name
        FROM user_cons_columns a
        JOIN user_constraints b ON a.constraint_name = b.constraint_name
        WHERE a.table_name = :tabla
          AND b.constraint_type = 'R'
          AND a.column_name IN :columnas
        """
    ).bindparams(sa.bindparam("columnas", expanding=True))
    fila = conn.execute(stmt, {"tabla": table.upper(), "columnas": [c.upper() for c in columnas]}).first()
    return fila[0] if fila else None


def _columna_existe(conn, table: str, columna: str) -> bool:
    stmt = sa.text(
        "SELECT 1 FROM user_tab_columns WHERE table_name = :tabla AND column_name = :columna"
    )
    return conn.execute(stmt, {"tabla": table.upper(), "columna": columna.upper()}).first() is not None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    fk_name = _fk_constraint_name(conn, TABLA, ("empresa_id", "nombre_empresa"))
    if fk_name:
        conn.exec_driver_sql(f'ALTER TABLE {TABLA} DROP CONSTRAINT "{fk_name}"')

    if _columna_existe(conn, TABLA, "empresa_id") and not _columna_existe(conn, TABLA, "nombre_empresa"):
        conn.exec_driver_sql(f"ALTER TABLE {TABLA} RENAME COLUMN empresa_id TO nombre_empresa")

    conn.exec_driver_sql(f"ALTER TABLE {TABLA} MODIFY (nombre_empresa VARCHAR2(200))")


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    conn.exec_driver_sql(f"ALTER TABLE {TABLA} MODIFY (nombre_empresa NUMBER)")
    conn.exec_driver_sql(f"ALTER TABLE {TABLA} RENAME COLUMN nombre_empresa TO empresa_id")

    op.create_foreign_key(
        "fk_bitacora_empresa_id",
        TABLA, "mercadeo_crm_empresas", ["empresa_id"], ["id"],
    )
