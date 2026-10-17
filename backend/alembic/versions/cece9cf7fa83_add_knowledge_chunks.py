"""add knowledge chunks

Revision ID: cece9cf7fa83
Revises: ec25901640a9
Create Date: 2026-09-15 16:20:19.807445

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "cece9cf7fa83"
down_revision: Union[str, Sequence[str], None] = "ec25901640a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "knowledge_chunks",
        sa.Column("chunk_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.product_id"],
        ),
        sa.PrimaryKeyConstraint("chunk_id"),
    )

    op.create_index(
        op.f("ix_knowledge_chunks_product_id"),
        "knowledge_chunks",
        ["product_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_knowledge_chunks_product_id"),
        table_name="knowledge_chunks",
    )

    op.drop_table("knowledge_chunks")