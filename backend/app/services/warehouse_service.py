from sqlalchemy.orm import Session

from app.models.inventory import Inventory


class WarehouseService:

    @staticmethod
    def select_warehouse(
        db: Session,
        product_id: int,
        requested_quantity: int,
    ) -> Inventory | None:

        inventories = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == product_id,
                Inventory.quantity >= requested_quantity,
            )
            .all()
        )

        if not inventories:
            return None

        best_inventory = None
        best_score = -1.0

        for inventory in inventories:

            # Current prototype:
            # Real delivery/distance signals can be added later.
            delivery_fit = 1.0
            distance_fit = 1.0

            inventory_availability = min(
                inventory.quantity / requested_quantity,
                1.0,
            )

            score = (
                0.50 * delivery_fit
                + 0.30 * inventory_availability
                + 0.20 * distance_fit
            )

            if score > best_score:
                best_score = score
                best_inventory = inventory

        return best_inventory