from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base


class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"

    reservation_id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    inventory_id: Mapped[int] = mapped_column(
        ForeignKey("inventory.inventory_id"),
        nullable=False,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ACTIVE",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    inventory = relationship(
        "Inventory",
        back_populates="reservations",
    )

    order = relationship(
        "Order",
        back_populates="reservations",
    )