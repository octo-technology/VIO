"""create telemetry table

Revision ID: 9a3bcc873799
Revises:
Create Date: 2021-08-20 12:20:54.427254

"""
import sqlalchemy as sa
from alembic import op
# revision identifiers, used by Alembic.
from sqlalchemy.dialects import postgresql

revision = '9a3bcc873799'
down_revision = '2c9a089cc2d5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'telemetry',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('device_id', sa.TEXT, nullable=False),
        sa.Column('business_decision', sa.TEXT, nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP, nullable=False),
        schema='iothub'
    )


def downgrade():
    op.drop_table('telemetry', schema='iothub')
