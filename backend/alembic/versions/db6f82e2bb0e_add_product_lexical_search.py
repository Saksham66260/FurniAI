"""add product lexical search

Revision ID: db6f82e2bb0e
Revises: 8f5e9cc3c9d8
Create Date: 2026-09-10 11:19:58.454472

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql


revision: str = "db6f82e2bb0e"
down_revision: Union[str, Sequence[str], None] = "8f5e9cc3c9d8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add the TSVECTOR column.
    op.add_column(
        "products",
        sa.Column(
            "search_vector",
            sa.dialects.postgresql.TSVECTOR(),
            nullable=True,
        ),
    )

    # 2. Populate search_vector for existing products.
    op.execute(
        """
        UPDATE products
        SET search_vector =
            to_tsvector(
                'english',
                concat_ws(
                    ' ',
                    sku,
                    name,
                    description,
                    category,
                    subcategory,
                    material,
                    style,
                    color,
                    array_to_string(features, ' ')
                )
            )
        """
    )

    # 3. Create a GIN index for fast lexical search.
    op.create_index(
        "ix_products_search_vector",
        "products",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_products_search_vector",
        table_name="products",
    )

    op.drop_column(
        "products",
        "search_vector",
    )