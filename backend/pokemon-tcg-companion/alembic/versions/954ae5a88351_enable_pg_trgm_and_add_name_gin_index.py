"""enable pg_trgm and add GIN index on refcard.name

Revision ID: 954ae5a88351
Revises: 04b530f5d463
Create Date: 2026-02-22 00:00:00.000000
"""

from alembic import op

revision = "954ae5a88351"
down_revision = "04b530f5d463"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX ix_refcard_name_trgm ON refcard USING GIN (name gin_trgm_ops)"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_refcard_name_trgm")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
