from sqlalchemy import Numeric, String, Text, Float
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from app.db.base import Base
from pgvector.sqlalchemy import Vector


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    sku: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    subcategory: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
    )

    material: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    style: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    color: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    rating: Mapped[float] = mapped_column(
        Float,
    )

    review_count: Mapped[int] = mapped_column()

    features: Mapped[list[str]] = mapped_column(
        ARRAY(String),
    )

    dimensions: Mapped[dict] = mapped_column(
        JSONB,
    )

    weight: Mapped[float] = mapped_column(
        Float,
    )

    description: Mapped[str] = mapped_column(
        Text,
    )

    attributes: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
    )
    search_vector: Mapped[object | None] = mapped_column(
    TSVECTOR,
    nullable=True,
    )
    embedding: Mapped[list[float] | None] = mapped_column(
    Vector(384),
    nullable=True,
    )

    inventory = relationship(
        "Inventory",
        back_populates="product",
    )

    order_items = relationship(
        "OrderItem",
        back_populates="product",
    )

    cart_items = relationship(
    "CartItem",
    back_populates="product",
    )