"""add card model
Revision ID: 2adf5d447517
Revises: 
Create Date: 2026-02-21 02:18:02.855720
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "2adf5d447517"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('card',
        sa.Column('tcg_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('card')