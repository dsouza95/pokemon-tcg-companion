"""ref card make image optional tcg id unique
Revision ID: 04b530f5d463
Revises: 75518cffa3bd
Create Date: 2026-02-22 13:54:24.907675
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "04b530f5d463"
down_revision = "75518cffa3bd"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("refcard", "image_url", existing_type=sa.VARCHAR(), nullable=True)
    op.drop_index(op.f("ix_refcard_tcg_id"), table_name="refcard")
    op.create_index(op.f("ix_refcard_tcg_id"), "refcard", ["tcg_id"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_refcard_tcg_id"), table_name="refcard")
    op.create_index(op.f("ix_refcard_tcg_id"), "refcard", ["tcg_id"], unique=False)
    op.alter_column("refcard", "image_url", existing_type=sa.VARCHAR(), nullable=False)
