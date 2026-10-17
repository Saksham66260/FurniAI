from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    preferred_style: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    preferred_material: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    min_price: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    max_price: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="preferences",
    )