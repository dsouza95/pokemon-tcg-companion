"""add card ref card model
Revision ID: 75518cffa3bd
Revises: 84c8c29e1fd8
Create Date: 2026-02-22 12:31:55.103089
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "75518cffa3bd"
down_revision = "84c8c29e1fd8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "refcard",
        sa.Column("tcg_id", sa.String(), nullable=False),
        sa.Column("tcg_local_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("set_id", sa.String(), nullable=False),
        sa.Column("set_name", sa.String(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_refcard_set_id"), "refcard", ["set_id"], unique=False)
    op.create_index(op.f("ix_refcard_tcg_id"), "refcard", ["tcg_id"], unique=False)
    op.create_index(
        op.f("ix_refcard_tcg_local_id"), "refcard", ["tcg_local_id"], unique=False
    )
    op.add_column("card", sa.Column("ref_card_id", sa.Uuid(), nullable=True))
    op.create_index(op.f("ix_card_ref_card_id"), "card", ["ref_card_id"], unique=False)
    op.create_foreign_key(
        "fk_card_ref_card_id", "card", "refcard", ["ref_card_id"], ["id"]
    )
    op.drop_column("card", "tcg_id")
    op.drop_column("card", "name")


def downgrade():
    op.add_column(
        "card", sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "card", sa.Column("tcg_id", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.drop_constraint("fk_card_ref_card_id", "card", type_="foreignkey")
    op.drop_index(op.f("ix_card_ref_card_id"), table_name="card")
    op.drop_column("card", "ref_card_id")
    op.drop_index(op.f("ix_refcard_tcg_local_id"), table_name="refcard")
    op.drop_index(op.f("ix_refcard_tcg_id"), table_name="refcard")
    op.drop_index(op.f("ix_refcard_set_id"), table_name="refcard")
    op.drop_table("refcard")
