"""add user_id and make card fields optional
Revision ID: 84c8c29e1fd8
Revises: 2adf5d447517
Create Date: 2026-02-22 00:40:01.931016
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "84c8c29e1fd8"
down_revision = '2adf5d447517'
branch_labels = None
depends_on = None



def upgrade():
    op.add_column('card', sa.Column('image_path', sa.String(), nullable=False))
    op.add_column('card', sa.Column('user_id', sa.String(), nullable=False))
    op.alter_column('card', 'tcg_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('card', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_index(op.f('ix_card_user_id'), 'card', ['user_id'], unique=False)
    op.drop_column('card', 'image_url')


def downgrade():
    op.add_column('card', sa.Column('image_url', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_card_user_id'), table_name='card')
    op.alter_column('card', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('card', 'tcg_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('card', 'user_id')
    op.drop_column('card', 'image_path')
