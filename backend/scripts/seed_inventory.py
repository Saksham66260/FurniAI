from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory


def seed_inventory():
    db = SessionLocal()

    try:
        products = db.scalars(select(Product)).all()
        warehouses = db.scalars(select(Warehouse)).all()

        print(f"Products found: {len(products)}")
        print(f"Warehouses found: {len(warehouses)}")

        if not products:
            print("No products found.")
            return

        if not warehouses:
            print("No warehouses found.")
            return

        existing_pairs = set(
            db.query(Inventory.product_id, Inventory.warehouse_id).all()
        )

        inventory_rows = []

        for product in products:
            for warehouse in warehouses:
                pair = (product.product_id, warehouse.warehouse_id)

                if pair in existing_pairs:
                    continue

                inventory_rows.append(
                    Inventory(
                        product_id=product.product_id,
                        warehouse_id=warehouse.warehouse_id,
                        quantity=20,
                    )
                )

        db.add_all(inventory_rows)
        db.commit()

        print(f"Created {len(inventory_rows)} new inventory rows.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_inventory()