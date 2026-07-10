"""agregar fk responsable_id de servicios a intranet_usuarios

Revision ID: aa6c23257c62
Revises: 270c00380275
Create Date: 2026-07-10 10:22:22.936869

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'aa6c23257c62'
down_revision: Union[str, Sequence[str], None] = '270c00380275'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        'fk_servicio_responsable_id',
        'mercadeo_crm_servicios', 'intranet_usuarios', ['responsable_id'], ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_servicio_responsable_id', 'mercadeo_crm_servicios', type_='foreignkey')
