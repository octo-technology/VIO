"""Add a column config, item_id

Revision ID: 9d07ddc2955c
Revises: 9a3bcc873799
Create Date: 2021-08-20 12:30:52.254609

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9d07ddc2955c'
down_revision = '9a3bcc873799'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('telemetry', sa.Column('item_id', sa.TEXT, nullable=True), schema='iothub')
    op.add_column('telemetry', sa.Column('config', sa.TEXT, nullable=True), schema='iothub')


def downgrade():
    op.drop_column('telemetry', 'item_id', schema='iothub')
    op.drop_column('telemetry', 'config', schema='iothub')
