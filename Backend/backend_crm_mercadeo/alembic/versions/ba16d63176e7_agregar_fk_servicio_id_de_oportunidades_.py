"""agregar fk servicio_id de oportunidades a mercadeo_crm_servicios

Revision ID: ba16d63176e7
Revises: 5d9707e46a05
Create Date: 2026-07-10 09:40:34.344941

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ba16d63176e7'
down_revision: Union[str, Sequence[str], None] = '5d9707e46a05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# NOTA: igual que en las migraciones anteriores de intranet_planliga, el
# autogenerate volvio a detectar las columnas "no mapeadas" de esa tabla
# externa como si sobraran y quiso eliminarlas junto con el indice
# uk_planliga_tipo_documento. Ese bloque se removio a mano; solo se deja
# la FK que realmente se queria agregar (esta migracion no toca
# intranet_planliga para nada).


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        'fk_oportunidad_servicio_id',
        'mercadeo_crm_oportunidades', 'mercadeo_crm_servicios', ['servicio_id'], ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_oportunidad_servicio_id', 'mercadeo_crm_oportunidades', type_='foreignkey')
