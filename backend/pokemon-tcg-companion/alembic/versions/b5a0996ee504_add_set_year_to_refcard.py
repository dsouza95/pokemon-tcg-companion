"""add set_year to refcard
Revision ID: b5a0996ee504
Revises: 94be8bedf4cf
Create Date: 2026-03-01 14:31:17.093108
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "b5a0996ee504"
down_revision = "94be8bedf4cf"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("refcard", sa.Column("set_year", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("refcard", "set_year")
