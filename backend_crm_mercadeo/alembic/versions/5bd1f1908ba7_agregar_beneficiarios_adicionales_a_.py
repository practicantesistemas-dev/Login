"""agregar beneficiarios adicionales a servicios

Revision ID: 5bd1f1908ba7
Revises: 75ac5f04e5cc
Create Date: 2026-07-16 15:57:57.428501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bd1f1908ba7'
down_revision: Union[str, Sequence[str], None] = '75ac5f04e5cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "mercadeo_crm_servicios",
        sa.Column("beneficiarios_adicionales", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("mercadeo_crm_servicios", "beneficiarios_adicionales")
