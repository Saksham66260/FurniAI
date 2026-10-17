from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
    )

    location: Mapped[str] = mapped_column(
        String(255),
    )

    inventory = relationship(
        "Inventory",
        back_populates="warehouse",
    )

    shipments = relationship(
        "Shipment",
        back_populates="warehouse",
    )