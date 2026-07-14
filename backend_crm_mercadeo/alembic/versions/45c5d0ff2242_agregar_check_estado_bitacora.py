"""agregar check estado bitacora

Revision ID: 45c5d0ff2242
Revises: 3e5f76625827
Create Date: 2026-07-14 13:13:43.456520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45c5d0ff2242'
down_revision: Union[str, Sequence[str], None] = '3e5f76625827'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_mercadeo_crm_bitacora_estado",
        "mercadeo_crm_bitacora",
        "estado IN ('pendiente', 'realizado')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_mercadeo_crm_bitacora_estado", "mercadeo_crm_bitacora", type_="check"
    )
