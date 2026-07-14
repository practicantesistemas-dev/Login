"""agregar check tipo contacto

Revision ID: 8e8cc45d8e4c
Revises: 45c5d0ff2242
Create Date: 2026-07-14 15:42:02.771175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e8cc45d8e4c'
down_revision: Union[str, Sequence[str], None] = '45c5d0ff2242'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_mercadeo_crm_contactos_tipo_contacto",
        "mercadeo_crm_contactos",
        "tipo_contacto IS NULL OR tipo_contacto IN ('Cliente', 'Prospecto')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_mercadeo_crm_contactos_tipo_contacto", "mercadeo_crm_contactos", type_="check"
    )
