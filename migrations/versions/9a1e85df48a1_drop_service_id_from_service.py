"""drop service_id from service

Revision ID: 9a1e85df48a1
Revises: 052f7b817bbd
Create Date: 2026-04-23 21:58:05.909435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a1e85df48a1'
down_revision = '052f7b817bbd'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('service', 'service_id')


def downgrade():
    op.add_column(
        'service',
        sa.Column('service_id', sa.Integer(), nullable=False, server_default='0'),
    )
    op.alter_column('service', 'service_id', server_default=None)
