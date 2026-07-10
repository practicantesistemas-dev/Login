"""agregar fecha_creacion y fecha_actualizacion

Revision ID: 6013554ffe59
Revises: 4e379ceb9f70
Create Date: 2026-07-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6013554ffe59'
down_revision: Union[str, Sequence[str], None] = '4e379ceb9f70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = [
    "mercadeo_crm_contactos",
    "mercadeo_crm_oportunidades",
    "mercadeo_crm_empresas",
    "mercadeo_crm_campanas",
    "mercadeo_crm_proveedores",
    "mercadeo_crm_servicios",
    "mercadeo_crm_actividad",
]


def upgrade() -> None:
    """Upgrade schema."""
    for table in TABLES:
        op.add_column(table, sa.Column('fecha_creacion', sa.DateTime(), nullable=True))
        op.add_column(table, sa.Column('fecha_actualizacion', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    for table in TABLES:
        op.drop_column(table, 'fecha_actualizacion')
        op.drop_column(table, 'fecha_creacion')
