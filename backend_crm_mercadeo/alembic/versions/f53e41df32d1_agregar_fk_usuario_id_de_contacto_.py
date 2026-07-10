"""agregar fk usuario_id de contacto_etiqueta y campana_segmento a intranet_usuarios

Revision ID: f53e41df32d1
Revises: d4b4c115cba4
Create Date: 2026-07-10 10:48:29.923935

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f53e41df32d1'
down_revision: Union[str, Sequence[str], None] = 'd4b4c115cba4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# NOTA: igual que en las migraciones anteriores, el autogenerate detecto
# las columnas "no mapeadas" de intranet_planliga e intranet_usuarios
# (tablas externas, mapeadas aqui solo con id) como si sobraran y quiso
# eliminarlas junto con el indice uk_planliga_tipo_documento. Ese bloque
# se removio a mano; esta migracion no toca intranet_planliga ni
# intranet_usuarios para nada.


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        'fk_campana_seg_usuario_id',
        'mercadeo_crm_campana_segmento', 'intranet_usuarios', ['usuario_id'], ['id'],
    )
    op.create_foreign_key(
        'fk_contacto_etiq_usuario_id',
        'mercadeo_crm_contacto_etiqueta', 'intranet_usuarios', ['usuario_id'], ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_contacto_etiq_usuario_id', 'mercadeo_crm_contacto_etiqueta', type_='foreignkey')
    op.drop_constraint('fk_campana_seg_usuario_id', 'mercadeo_crm_campana_segmento', type_='foreignkey')
