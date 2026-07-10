"""agregar fk plan_liga_titular_id y titular_id a intranet_planliga

Revision ID: 3259e2d281f2
Revises: b69ada5831d9
Create Date: 2026-07-10 09:17:16.734201

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3259e2d281f2'
down_revision: Union[str, Sequence[str], None] = 'b69ada5831d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# NOTA: intranet_planliga es una tabla externa (modulo Integraciones) con
# muchas mas columnas de las que este proyecto mapea. El autogenerate de
# Alembic detecto esas columnas "no mapeadas" como si sobraran y quiso
# eliminarlas (junto con el indice uk_planliga_tipo_documento); ese bloque
# se removio a mano de esta migracion porque hubiera borrado datos reales.
# Solo se dejan las dos FKs que realmente se querian agregar.


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        'fk_bitacora_titular_id', 'mercadeo_crm_bitacora', 'intranet_planliga', ['titular_id'], ['id']
    )
    op.create_foreign_key(
        'fk_oportunidad_titular_id',
        'mercadeo_crm_oportunidades', 'intranet_planliga', ['plan_liga_titular_id'], ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_oportunidad_titular_id', 'mercadeo_crm_oportunidades', type_='foreignkey')
    op.drop_constraint('fk_bitacora_titular_id', 'mercadeo_crm_bitacora', type_='foreignkey')
