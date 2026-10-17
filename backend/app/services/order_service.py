import json

from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.cache.redis import redis_client

from app.models.cart import Cart
from app.models.idempotency_key import IdempotencyKey
from app.models.inventory import Inventory
from app.models.inventory_reservation import InventoryReservation
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.user import User

from app.services.warehouse_service import WarehouseService


IDEMPOTENCY_TTL = 900


class OrderService:

    @staticmethod
    def create_order(
        db: Session,
        user_id: int,
        idempotency_key: str,
    ) -> Order:

        redis_key = f"idempotency:{idempotency_key}"

        # Try to claim the idempotency key atomically.
        claimed = redis_client.set(
            redis_key,
            "PROCESSING",
            nx=True,
            ex=IDEMPOTENCY_TTL,
        )

        if not claimed:
            cached_response = redis_client.get(redis_key)

            if cached_response and cached_response != "PROCESSING":
                response_data = json.loads(cached_response)

                return OrderService._response_to_order(
                    db=db,
                    response_data=response_data,
                )

            raise ValueError(
                "Request with this Idempotency-Key is already being processed"
            )

        try:

            # -------------------------------------------------
            # 1. Validate user
            # -------------------------------------------------

            user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if user is None:
                raise ValueError("User not found")

            # -------------------------------------------------
            # 2. Get user's cart
            # -------------------------------------------------

            cart = (
                db.query(Cart)
                .filter(Cart.user_id == user_id)
                .first()
            )

            if cart is None:
                raise ValueError("Cart not found")

            if not cart.items:
                raise ValueError("Cart is empty")

            # -------------------------------------------------
            # 3. Create order
            # -------------------------------------------------

            order = Order(
                user_id=user_id,
                status="PENDING",
                total_amount=Decimal("0.00"),
            )

            db.add(order)
            db.flush()

            total_amount = Decimal("0.00")

            # -------------------------------------------------
            # 4. Process every cart item
            # -------------------------------------------------

            for cart_item in cart.items:

                product = cart_item.product

                # ---------------------------------------------
                # Select suitable warehouse
                # ---------------------------------------------

                inventory = WarehouseService.select_warehouse(
                    db=db,
                    product_id=cart_item.product_id,
                    requested_quantity=cart_item.quantity,
                )

                if inventory is None:
                    raise ValueError(
                        f"OUT_OF_STOCK: product {cart_item.product_id}"
                    )

                # ---------------------------------------------
                # Lock inventory row
                # ---------------------------------------------

                inventory = (
                    db.query(Inventory)
                    .filter(
                        Inventory.inventory_id
                        == inventory.inventory_id
                    )
                    .with_for_update()
                    .first()
                )

                if inventory is None:
                    raise ValueError(
                        f"Inventory not found for product "
                        f"{cart_item.product_id}"
                    )

                # ---------------------------------------------
                # Re-check stock AFTER acquiring lock
                # ---------------------------------------------

                if inventory.quantity < cart_item.quantity:
                    raise ValueError(
                        f"OUT_OF_STOCK: product "
                        f"{cart_item.product_id}"
                    )

                # ---------------------------------------------
                # Reserve inventory
                # ---------------------------------------------

                inventory.quantity -= cart_item.quantity

                # ---------------------------------------------
                # Create order item
                # ---------------------------------------------

                unit_price = Decimal(str(product.price))

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    unit_price=unit_price,
                )

                db.add(order_item)

                # ---------------------------------------------
                # Calculate order total
                # ---------------------------------------------

                total_amount += (
                    unit_price * cart_item.quantity
                )

                # ---------------------------------------------
                # Create inventory reservation
                # ---------------------------------------------

                reservation = InventoryReservation(
                    inventory_id=inventory.inventory_id,
                    order_id=order.id,
                    quantity=cart_item.quantity,
                    status="ACTIVE",
                )

                db.add(reservation)

            # -------------------------------------------------
            # 5. Set final order total
            # -------------------------------------------------

            order.total_amount = total_amount

            # -------------------------------------------------
            # 6. Commit order + inventory changes
            # -------------------------------------------------

            db.commit()
            db.refresh(order)

            # -------------------------------------------------
            # 7. Build response
            # -------------------------------------------------

            response_data = {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "total_amount": float(order.total_amount),
                "items": [
                    {
                        "order_item_id": item.order_item_id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                    }
                    for item in order.items
                ],
            }

            # -------------------------------------------------
            # 8. Persist idempotency record
            # -------------------------------------------------

            idempotency_record = IdempotencyKey(
                key=idempotency_key,
                status="COMPLETED",
                created_at=datetime.utcnow(),
                expires_at=(
                    datetime.utcnow()
                    + timedelta(seconds=IDEMPOTENCY_TTL)
                ),
                response_data=json.dumps(response_data),
            )

            db.add(idempotency_record)
            db.commit()

            # -------------------------------------------------
            # 9. Cache completed response in Redis
            # -------------------------------------------------

            redis_client.set(
                redis_key,
                json.dumps(response_data),
                ex=IDEMPOTENCY_TTL,
            )

            return order

        except Exception:

            # Rollback database changes
            db.rollback()

            # Remove PROCESSING idempotency key
            redis_client.delete(redis_key)

            raise

    @staticmethod
    def _response_to_order(
        db: Session,
        response_data: dict,
    ) -> Order:

        order = (
            db.query(Order)
            .filter(
                Order.id == response_data["id"]
            )
            .first()
        )

        if order is None:
            raise ValueError(
                "Previously created order could not be found"
            )

        return order

    @staticmethod
    def get_order(
        db: Session,
        order_id: int,
    ) -> Order | None:

        return (
            db.query(Order)
            .filter(
                Order.id == order_id
            )
            .first()
        )