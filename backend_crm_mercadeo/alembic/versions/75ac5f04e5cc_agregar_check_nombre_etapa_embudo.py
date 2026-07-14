"""agregar check nombre etapa embudo

Revision ID: 75ac5f04e5cc
Revises: 8e8cc45d8e4c
Create Date: 2026-07-14 16:50:11.753372

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75ac5f04e5cc'
down_revision: Union[str, Sequence[str], None] = '8e8cc45d8e4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ENABLE NOVALIDATE: hay filas de prueba previas (p.ej. "Contacto inicial")
    # que no cumplen el nuevo set de etapas. No se validan las filas
    # existentes, pero el constraint queda activo para inserts/updates nuevos.
    op.execute(
        "ALTER TABLE mercadeo_crm_etapas_embudo "
        "ADD CONSTRAINT ck_mercadeo_crm_etapas_embudo_nombre "
        "CHECK (nombre IN ('Lead', 'Primer Contacto', 'Reunión', 'Cotización', "
        "'Negociación', 'Ganada', 'Perdida')) "
        "ENABLE NOVALIDATE"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_mercadeo_crm_etapas_embudo_nombre", "mercadeo_crm_etapas_embudo", type_="check"
    )
