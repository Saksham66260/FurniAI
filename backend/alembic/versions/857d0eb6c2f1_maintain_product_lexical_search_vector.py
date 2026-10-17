"""maintain product lexical search vector

Revision ID: 857d0eb6c2f1
Revises: db6f82e2bb0e
"""

from typing import Sequence, Union

from alembic import op


revision: str = "857d0eb6c2f1"
down_revision: Union[str, Sequence[str], None] = "db6f82e2bb0e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE FUNCTION update_product_search_vector()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            NEW.search_vector :=
                to_tsvector(
                    'english',
                    concat_ws(
                        ' ',
                        NEW.sku,
                        NEW.name,
                        NEW.description,
                        NEW.category,
                        NEW.subcategory,
                        NEW.material,
                        NEW.style,
                        NEW.color,
                        array_to_string(NEW.features, ' ')
                    )
                );

            RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE TRIGGER products_search_vector_trigger
        BEFORE INSERT OR UPDATE OF
            sku,
            name,
            description,
            category,
            subcategory,
            material,
            style,
            color,
            features
        ON products
        FOR EACH ROW
        EXECUTE FUNCTION update_product_search_vector();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS products_search_vector_trigger
        ON products;
        """
    )

    op.execute(
        """
        DROP FUNCTION IF EXISTS update_product_search_vector();
        """
    )