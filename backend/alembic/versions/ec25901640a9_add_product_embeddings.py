"""add product embeddings

Revision ID: ec25901640a9
Revises: 857d0eb6c2f1
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = "ec25901640a9"
down_revision: Union[str, Sequence[str], None] = "857d0eb6c2f1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "embedding",
            Vector(384),
            nullable=True,
        ),
    )

    op.execute(
        """
        CREATE INDEX ix_products_embedding_hnsw
        ON products
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_products_embedding_hnsw",
        table_name="products",
    )

    op.drop_column("products", "embedding")