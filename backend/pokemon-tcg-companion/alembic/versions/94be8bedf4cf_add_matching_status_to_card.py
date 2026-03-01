"""add matching_status to card
Revision ID: 94be8bedf4cf
Revises: 954ae5a88351
Create Date: 2026-02-28 00:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "94be8bedf4cf"
down_revision = "954ae5a88351"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "card",
        sa.Column(
            "matching_status",
            sa.String(),
            nullable=False,
            server_default="pending",
        ),
    )


def downgrade():
    op.drop_column("card", "matching_status")
