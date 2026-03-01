"""add tcgset table and migrate refcard set columns

Revision ID: e6ef42a47d89
Revises: b5a0996ee504
Create Date: 2026-03-01 14:53:49.859114
"""

import sqlalchemy as sa

from alembic import op

revision = "e6ef42a47d89"
down_revision = "b5a0996ee504"
branch_labels = None
depends_on = None


def upgrade():
    # Create the tcgset table
    op.create_table(
        "tcgset",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tcg_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tcgset_tcg_id", "tcgset", ["tcg_id"], unique=True)
    op.create_index("ix_tcgset_year", "tcgset", ["year"])

    # Populate tcgset from existing refcard data (no-op if refcard is empty)
    op.execute("""
        INSERT INTO tcgset (id, tcg_id, name, year)
        SELECT gen_random_uuid(), set_id, MAX(set_name), MAX(set_year)
        FROM refcard
        WHERE set_id IS NOT NULL
        GROUP BY set_id
    """)

    # Add a temporary UUID column to hold the new FK value
    op.add_column("refcard", sa.Column("new_set_id", sa.Uuid(), nullable=True))

    # Map each refcard row to its corresponding tcgset row
    op.execute("""
        UPDATE refcard
        SET new_set_id = (
            SELECT id FROM tcgset WHERE tcgset.tcg_id = refcard.set_id
        )
    """)

    # Drop old set columns and the string set_id index
    op.drop_index("ix_refcard_set_id", table_name="refcard")
    op.drop_column("refcard", "set_id")
    op.drop_column("refcard", "set_name")
    op.drop_column("refcard", "set_year")

    # Rename new_set_id → set_id and enforce NOT NULL + FK
    op.alter_column("refcard", "new_set_id", new_column_name="set_id")
    op.alter_column("refcard", "set_id", nullable=False)
    op.create_foreign_key("fk_refcard_set_id", "refcard", "tcgset", ["set_id"], ["id"])
    op.create_index("ix_refcard_set_id", "refcard", ["set_id"])


def downgrade():
    op.drop_index("ix_refcard_set_id", table_name="refcard")
    op.drop_constraint("fk_refcard_set_id", "refcard", type_="foreignkey")
    op.alter_column("refcard", "set_id", new_column_name="new_set_id")

    op.add_column("refcard", sa.Column("set_id", sa.String(), nullable=True))
    op.add_column("refcard", sa.Column("set_name", sa.String(), nullable=True))
    op.add_column("refcard", sa.Column("set_year", sa.Integer(), nullable=True))

    op.execute("""
        UPDATE refcard
        SET set_id = tcgset.tcg_id,
            set_name = tcgset.name,
            set_year = tcgset.year
        FROM tcgset
        WHERE tcgset.id = refcard.new_set_id
    """)

    op.drop_column("refcard", "new_set_id")
    op.create_index("ix_refcard_set_id", "refcard", ["set_id"])
    op.drop_index("ix_tcgset_year", table_name="tcgset")
    op.drop_table("tcgset")
