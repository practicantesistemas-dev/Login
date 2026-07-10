"""agregar fk usuario_id de importaciones a intranet_usuarios

Revision ID: d4b4c115cba4
Revises: aa6c23257c62
Create Date: 2026-07-10 10:32:01.960776

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd4b4c115cba4'
down_revision: Union[str, Sequence[str], None] = 'aa6c23257c62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


        
def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        'fk_importacion_usuario_id',
        'mercadeo_crm_importaciones', 'intranet_usuarios', ['usuario_id'], ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_importacion_usuario_id', 'mercadeo_crm_importaciones', type_='foreignkey')
