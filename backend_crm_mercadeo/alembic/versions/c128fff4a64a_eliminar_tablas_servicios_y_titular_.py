"""eliminar tablas servicios y titular_servicios, repuntar fk oportunidades a tipo_plan

Revision ID: c128fff4a64a
Revises: 5bd1f1908ba7
Create Date: 2026-07-24 09:16:17.672682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c128fff4a64a'
down_revision: Union[str, Sequence[str], None] = '5bd1f1908ba7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# mercadeo_crm_servicios y mercadeo_crm_titular_servicios se reemplazan por
# intranet_planliga_tipo_plan (tabla externa del modulo Integraciones que
# ya existe en la base de datos: un titular ahora tiene un unico tipo de
# plan via intranet_planliga.tipo_plan_id, columna que igualmente ya existe
# y no se crea aqui). mercadeo_crm_oportunidades.servicio_id se repunta a
# esa tabla en lugar de a la que se elimina.
#
# Las secuencias seq_servicios/seq_titular_servicios (creadas en la
# migracion 4e379ceb9f70 para autonumerar via trigger BEFORE INSERT) no se
# eliminan solas al hacer DROP TABLE en Oracle porque son objetos
# independientes; se eliminan a mano igual que se crearon, con
# exec_driver_sql idempotente.


def _drop_if_exists(conn, kind: str, name: str, missing_error: int) -> None:
    conn.exec_driver_sql(
        f"""
        BEGIN
            EXECUTE IMMEDIATE 'DROP {kind} {name}';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -{missing_error} THEN
                    RAISE;
                END IF;
        END;
        """
    )


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    op.drop_constraint('fk_oportunidad_servicio_id', 'mercadeo_crm_oportunidades', type_='foreignkey')

    op.drop_table('mercadeo_crm_titular_servicios')
    _drop_if_exists(conn, "SEQUENCE", "seq_titular_servicios", 2289)  # ORA-02289: sequence does not exist

    op.drop_table('mercadeo_crm_servicios')
    _drop_if_exists(conn, "SEQUENCE", "seq_servicios", 2289)

    op.create_foreign_key(
        'fk_oportunidad_servicio_id',
        'mercadeo_crm_oportunidades', 'intranet_planliga_tipo_plan', ['servicio_id'], ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    op.drop_constraint('fk_oportunidad_servicio_id', 'mercadeo_crm_oportunidades', type_='foreignkey')

    op.create_table('mercadeo_crm_servicios',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.Column('categoria', sa.String(length=100), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=True),
        sa.Column('max_beneficiarios', sa.Integer(), nullable=True),
        sa.Column('beneficiarios_adicionales', sa.Integer(), nullable=True),
        sa.Column('estado', sa.Boolean(), nullable=False),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key(
        'fk_servicio_responsable_id',
        'mercadeo_crm_servicios', 'intranet_usuarios', ['responsable_id'], ['id'],
    )

    op.create_table('mercadeo_crm_titular_servicios',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('planliga_id', sa.Integer(), nullable=True),
        sa.Column('servicio_id', sa.Integer(), nullable=True),
        sa.Column('fecha_asignacion', sa.DateTime(), nullable=True),
        sa.Column('estado', sa.String(length=30), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['servicio_id'], ['mercadeo_crm_servicios.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key(
        'fk_titular_serv_planliga_id',
        'mercadeo_crm_titular_servicios', 'intranet_planliga', ['planliga_id'], ['id'],
    )

    for table in ("mercadeo_crm_servicios", "mercadeo_crm_titular_servicios"):
        short = table.replace("mercadeo_crm_", "", 1)
        seq_name, trg_name = f"seq_{short}", f"trg_{short}_bi"
        _drop_if_exists(conn, "TRIGGER", trg_name, 4080)  # ORA-04080: trigger does not exist
        _drop_if_exists(conn, "SEQUENCE", seq_name, 2289)
        conn.exec_driver_sql(f"CREATE SEQUENCE {seq_name} START WITH 1 INCREMENT BY 1 NOCACHE")
        conn.exec_driver_sql(
            f"""
            CREATE OR REPLACE TRIGGER {trg_name}
            BEFORE INSERT ON {table}
            FOR EACH ROW
            WHEN (NEW.id IS NULL)
            BEGIN
                SELECT {seq_name}.NEXTVAL INTO :NEW.id FROM dual;
            END;
            """
        )

    op.create_foreign_key(
        'fk_oportunidad_servicio_id',
        'mercadeo_crm_oportunidades', 'mercadeo_crm_servicios', ['servicio_id'], ['id'],
    )
