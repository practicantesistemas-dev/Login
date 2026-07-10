"""agregar fk usuario_id de bitacora a intranet_usuarios

Revision ID: 2cc3829900e2
Revises: 9a1c7e5f3b02
Create Date: 2026-07-10 11:17:22.724386

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2cc3829900e2'
down_revision: Union[str, Sequence[str], None] = '9a1c7e5f3b02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        'fk_bitacora_usuario_id',
        'mercadeo_crm_bitacora', 'intranet_usuarios', ['usuario_id'], ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_bitacora_usuario_id', 'mercadeo_crm_bitacora', type_='foreignkey')
