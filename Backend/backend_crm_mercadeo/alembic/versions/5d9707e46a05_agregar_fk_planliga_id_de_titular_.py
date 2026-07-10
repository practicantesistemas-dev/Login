"""agregar fk planliga_id de titular_servicios a intranet_planliga

Revision ID: 5d9707e46a05
Revises: 3259e2d281f2
Create Date: 2026-07-10 09:32:40.222001

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '5d9707e46a05'
down_revision: Union[str, Sequence[str], None] = '3259e2d281f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# NOTA: igual que en 3259e2d281f2, el autogenerate detecto las columnas
# "no mapeadas" de intranet_planliga (tabla externa del modulo
# Integraciones) como si sobraran y quiso eliminarlas junto con el indice
# uk_planliga_tipo_documento. Ese bloque se removio a mano; solo se deja
# la FK que realmente se queria agregar.


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        'fk_titular_serv_planliga_id',
        'mercadeo_crm_titular_servicios', 'intranet_planliga', ['planliga_id'], ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_titular_serv_planliga_id', 'mercadeo_crm_titular_servicios', type_='foreignkey')
