"""
Concurrency Verification Test (Day 4 Unresolved Requirement)

Invariant:
When stock = 1 across all warehouses, and 2 simultaneous checkout requests
target the same product with distinct idempotency keys:
- EXACTLY 1 request must SUCCEED (Order created in PostgreSQL)
- EXACTLY 1 request must FAIL with OUT_OF_STOCK
- Post-test inventory quantity must be EXACTLY 0 (no overselling)
"""

import uuid
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import pytest
from sqlalchemy import text

from app.db.database import SessionLocal
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import User
from app.services.order_service import OrderService


def test_concurrent_checkout_prevents_overselling():
    db = SessionLocal()

    # 1. Choose an isolated test product (e.g., Product 100)
    test_product_id = 100
    test_user_id = 1

    try:
        # Ensure user 1 exists
        user = db.query(User).filter(User.id == test_user_id).first()
        assert user is not None, "Test user 1 must exist"

        product = db.query(Product).filter(Product.product_id == test_product_id).first()
        assert product is not None, f"Product {test_product_id} must exist"

        # 2. Force total stock across ALL warehouses for test_product_id to be EXACTLY 1
        # Warehouse 1: 1 item, Warehouse 2: 0 items
        db.query(Inventory).filter(Inventory.product_id == test_product_id).update({"quantity": 0})
        first_inventory = (
            db.query(Inventory)
            .filter(Inventory.product_id == test_product_id)
            .order_by(Inventory.warehouse_id.asc())
            .first()
        )
        assert first_inventory is not None, "At least one inventory row must exist"
        first_inventory.quantity = 1
        db.commit()

        # Verify initial total inventory is exactly 1
        total_initial_stock = sum(
            inv.quantity
            for inv in db.query(Inventory).filter(Inventory.product_id == test_product_id).all()
        )
        assert total_initial_stock == 1, f"Expected total initial stock = 1, got {total_initial_stock}"

        # 3. Setup user's cart with 1 unit of test_product_id
        cart = db.query(Cart).filter(Cart.user_id == test_user_id).first()
        if not cart:
            cart = Cart(user_id=test_user_id)
            db.add(cart)
            db.flush()

        # Clear existing items and set test item
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product_id,
            quantity=1,
        )
        db.add(cart_item)
        db.commit()

        # 4. Prepare concurrent execution
        idempotency_key_1 = f"race-test-A-{uuid.uuid4().hex[:8]}"
        idempotency_key_2 = f"race-test-B-{uuid.uuid4().hex[:8]}"

        results = {}

        def run_checkout(key: str):
            thread_db = SessionLocal()
            try:
                order = OrderService.create_order(
                    db=thread_db,
                    user_id=test_user_id,
                    idempotency_key=key,
                )
                return {"status": "SUCCESS", "order_id": order.id, "error": None}
            except Exception as exc:
                thread_db.rollback()
                return {"status": "FAILED", "order_id": None, "error": str(exc)}
            finally:
                thread_db.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(run_checkout, idempotency_key_1)
            future2 = executor.submit(run_checkout, idempotency_key_2)

            res1 = future1.result()
            res2 = future2.result()

        results[idempotency_key_1] = res1
        results[idempotency_key_2] = res2

        print("\n--- CONCURRENCY TEST RESULTS ---")
        print(f"Request A ({idempotency_key_1}): {res1}")
        print(f"Request B ({idempotency_key_2}): {res2}")

        statuses = [res1["status"], res2["status"]]
        success_count = statuses.count("SUCCESS")
        failed_count = statuses.count("FAILED")

        # 5. Assert exactly 1 succeeded and 1 failed with OUT_OF_STOCK
        assert success_count == 1, f"Expected exactly 1 SUCCESS, got {success_count}. Results: {results}"
        assert failed_count == 1, f"Expected exactly 1 FAILED, got {failed_count}. Results: {results}"

        failed_res = res1 if res1["status"] == "FAILED" else res2
        assert "OUT_OF_STOCK" in failed_res["error"], (
            f"Expected error to mention OUT_OF_STOCK, got: {failed_res['error']}"
        )

        # 6. Assert remaining stock across all warehouses is EXACTLY 0
        total_final_stock = sum(
            inv.quantity
            for inv in db.query(Inventory).filter(Inventory.product_id == test_product_id).all()
        )
        assert total_final_stock == 0, (
            f"Expected remaining total stock to be exactly 0, got {total_final_stock}!"
        )

        print(f"✓ Concurrency protection successfully verified!")
        print(f"  Success order: {[r['order_id'] for r in [res1, res2] if r['order_id']]}")
        print(f"  Failed reason: {failed_res['error']}")
        print(f"  Final remaining stock in DB: {total_final_stock}")

    finally:
        # Reset test product inventory to default reasonable amount (e.g. 50 in warehouse 1)
        first_inv = (
            db.query(Inventory)
            .filter(Inventory.product_id == test_product_id)
            .order_by(Inventory.warehouse_id.asc())
            .first()
        )
        if first_inv:
            first_inv.quantity = 50
            db.commit()
        db.close()


if __name__ == "__main__":
    test_concurrent_checkout_prevents_overselling()
