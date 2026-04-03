"""create iothub schema

Revision ID: 2c9a089cc2d5
Revises: 9d07ddc2955c
Create Date: 2023-01-27 16:21:14.303905

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '2c9a089cc2d5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("create schema iothub")


def downgrade():
    op.execute("drop schema iothub")
