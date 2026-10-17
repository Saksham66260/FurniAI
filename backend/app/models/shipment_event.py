from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ShipmentEvent(Base):
    __tablename__ = "shipment_events"

    event_id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("shipments.shipment_id"),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    shipment = relationship(
        "Shipment",
        back_populates="events",
    )