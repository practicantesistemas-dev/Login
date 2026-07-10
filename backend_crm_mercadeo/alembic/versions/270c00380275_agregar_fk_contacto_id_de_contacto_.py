"""agregar fk contacto_id de contacto_etiqueta a mercadeo_crm_contactos

Revision ID: 270c00380275
Revises: ba16d63176e7
Create Date: 2026-07-10 09:45:08.823705

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '270c00380275'
down_revision: Union[str, Sequence[str], None] = 'ba16d63176e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        'fk_contacto_etiqueta_contacto',
        'mercadeo_crm_contacto_etiqueta', 'mercadeo_crm_contactos', ['contacto_id'], ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_contacto_etiqueta_contacto', 'mercadeo_crm_contacto_etiqueta', type_='foreignkey')
