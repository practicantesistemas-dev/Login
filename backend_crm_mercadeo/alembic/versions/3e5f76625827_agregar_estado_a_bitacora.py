"""agregar estado a bitacora

Revision ID: 3e5f76625827
Revises: 6013554ffe59
Create Date: 2026-07-14 13:07:20.087279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e5f76625827'
down_revision: Union[str, Sequence[str], None] = '6013554ffe59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "mercadeo_crm_bitacora",
        sa.Column(
            "estado",
            sa.String(length=20),
            nullable=False,
            server_default="pendiente",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("mercadeo_crm_bitacora", "estado")
