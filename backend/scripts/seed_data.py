from decimal import Decimal

from app.db.database import SessionLocal
from app.models import Product, Warehouse, Inventory


PRODUCTS = [
    {
        "sku": "SOFA-001",
        "name": "Modern 3-Seater Sofa",
        "category": "Sofa",
        "subcategory": "3-Seater",
        "price": Decimal("899.99"),
        "material": "Fabric",
        "style": "Modern",
        "color": "Grey",
        "rating": 4.6,
        "review_count": 124,
        "features": ["Removable Cushions", "Stain Resistant"],
        "dimensions": {
            "width": 210,
            "depth": 90,
            "height": 85,
            "unit": "cm",
        },
        "weight": 48.0,
        "description": "A modern three-seater sofa with a comfortable fabric finish.",
        "attributes": {
            "seating_capacity": 3,
            "upholstery": "Fabric",
        },
    },
    {
        "sku": "DESK-001",
        "name": "Walnut Study Desk",
        "category": "Desk",
        "subcategory": "Study Desk",
        "price": Decimal("449.99"),
        "material": "Walnut",
        "style": "Minimalist",
        "color": "Brown",
        "rating": 4.5,
        "review_count": 87,
        "features": ["Cable Management", "Drawer"],
        "dimensions": {
            "width": 120,
            "depth": 60,
            "height": 75,
            "unit": "cm",
        },
        "weight": 25.0,
        "description": "A clean walnut study desk designed for focused work.",
        "attributes": {
            "drawer_count": 1,
            "cable_management": True,
        },
    },
    {
        "sku": "CHAIR-001",
        "name": "Ergonomic Office Chair",
        "category": "Chair",
        "subcategory": "Office Chair",
        "price": Decimal("299.99"),
        "material": "Mesh",
        "style": "Modern",
        "color": "Black",
        "rating": 4.7,
        "review_count": 231,
        "features": ["Adjustable Height", "Lumbar Support"],
        "dimensions": {
            "width": 65,
            "depth": 65,
            "height": 120,
            "unit": "cm",
        },
        "weight": 15.0,
        "description": "An ergonomic office chair with adjustable support.",
        "attributes": {
            "adjustable_height": True,
            "lumbar_support": True,
        },
    },
    {
        "sku": "BED-001",
        "name": "King Platform Bed",
        "category": "Bed",
        "subcategory": "Platform Bed",
        "price": Decimal("799.99"),
        "material": "Wood",
        "style": "Contemporary",
        "color": "Natural",
        "rating": 4.4,
        "review_count": 96,
        "features": ["Storage", "Solid Wood"],
        "dimensions": {
            "width": 193,
            "depth": 203,
            "height": 100,
            "unit": "cm",
        },
        "weight": 62.0,
        "description": "A contemporary king-size platform bed with built-in storage.",
        "attributes": {
            "mattress_size": "King",
            "storage": True,
            "headboard_type": "Panel",
        },
    },
    {
        "sku": "TABLE-001",
        "name": "Round Oak Dining Table",
        "category": "Table",
        "subcategory": "Dining Table",
        "price": Decimal("549.99"),
        "material": "Oak",
        "style": "Scandinavian",
        "color": "Natural",
        "rating": 4.8,
        "review_count": 156,
        "features": ["Solid Oak", "Seats Four"],
        "dimensions": {
            "width": 120,
            "depth": 120,
            "height": 75,
            "unit": "cm",
        },
        "weight": 35.0,
        "description": "A Scandinavian-style round dining table made from solid oak.",
        "attributes": {
            "seating_capacity": 4,
            "shape": "Round",
        },
    },
]


WAREHOUSES = [
    {
        "name": "Delhi Warehouse",
        "location": "Delhi",
    },
    {
        "name": "Mumbai Warehouse",
        "location": "Mumbai",
    },
]


def seed_data():
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. Create warehouses
        # ---------------------------------------------------------

        warehouses = []

        for warehouse_data in WAREHOUSES:
            warehouse = (
                db.query(Warehouse)
                .filter_by(name=warehouse_data["name"])
                .first()
            )

            if warehouse is None:
                warehouse = Warehouse(**warehouse_data)
                db.add(warehouse)

            warehouses.append(warehouse)

        db.flush()

        # ---------------------------------------------------------
        # 2. Create products
        # ---------------------------------------------------------

        products = []

        for product_data in PRODUCTS:
            product = (
                db.query(Product)
                .filter_by(sku=product_data["sku"])
                .first()
            )

            if product is None:
                product = Product(**product_data)
                db.add(product)

            products.append(product)

        db.flush()

        # ---------------------------------------------------------
        # 3. Create inventory
        # ---------------------------------------------------------

        quantities = [5, 8, 12, 6, 10]

        for product, quantity in zip(products, quantities):

            for warehouse_index, warehouse in enumerate(warehouses):

                existing_inventory = (
                    db.query(Inventory)
                    .filter_by(
                        product_id=product.product_id,
                        warehouse_id=warehouse.warehouse_id,
                    )
                    .first()
                )

                if existing_inventory is None:
                    inventory = Inventory(
                        product_id=product.product_id,
                        warehouse_id=warehouse.warehouse_id,
                        quantity=quantity
                        if warehouse_index == 0
                        else max(1, quantity - 2),
                    )

                    db.add(inventory)

        db.commit()

        print("Seed completed successfully.")
        print(f"Products: {len(products)}")
        print(f"Warehouses: {len(warehouses)}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()