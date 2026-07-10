"""agregar fk responsable_id de empresas contactos y oportunidades a intranet_usuarios

Revision ID: 9a1c7e5f3b02
Revises: f53e41df32d1
Create Date: 2026-07-10 11:10:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9a1c7e5f3b02'
down_revision: Union[str, Sequence[str], None] = 'f53e41df32d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# NOTA: escrita a mano (no via --autogenerate) porque la base de datos
# real todavia no tiene aplicadas las migraciones anteriores de esta
# cadena (alembic bloquea el autogenerate hasta que la DB este al dia).
# Sigue el mismo patron que las FKs anteriores hacia intranet_usuarios:
# solo agrega los constraints, no toca esa tabla externa para nada.


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        'fk_empresa_responsable_id',
        'mercadeo_crm_empresas', 'intranet_usuarios', ['responsable_id'], ['id'],
    )
    op.create_foreign_key(
        'fk_contacto_responsable_id',
        'mercadeo_crm_contactos', 'intranet_usuarios', ['responsable_id'], ['id'],
    )
    op.create_foreign_key(
        'fk_oportunidad_responsable_id',
        'mercadeo_crm_oportunidades', 'intranet_usuarios', ['responsable_id'], ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_oportunidad_responsable_id', 'mercadeo_crm_oportunidades', type_='foreignkey')
    op.drop_constraint('fk_contacto_responsable_id', 'mercadeo_crm_contactos', type_='foreignkey')
    op.drop_constraint('fk_empresa_responsable_id', 'mercadeo_crm_empresas', type_='foreignkey')
