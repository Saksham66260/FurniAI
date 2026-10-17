import random
from decimal import Decimal

from app.db.database import SessionLocal
from app.models import Product


random.seed(42)

TARGET_PRODUCTS = 5000


CATEGORIES = {
    "Sofa": {
        "subcategories": ["2-Seater", "3-Seater", "Sectional"],
        "materials": ["Fabric", "Leather", "Velvet"],
        "styles": ["Modern", "Contemporary", "Minimalist"],
        "colors": ["Grey", "Black", "Beige", "Blue"],
    },
    "Desk": {
        "subcategories": ["Study Desk", "Computer Desk", "Writing Desk"],
        "materials": ["Oak", "Walnut", "Engineered Wood"],
        "styles": ["Minimalist", "Modern", "Industrial"],
        "colors": ["Brown", "Black", "White", "Natural"],
    },
    "Chair": {
        "subcategories": ["Office Chair", "Dining Chair", "Lounge Chair"],
        "materials": ["Mesh", "Leather", "Fabric", "Wood"],
        "styles": ["Modern", "Contemporary", "Scandinavian"],
        "colors": ["Black", "Grey", "Brown", "White"],
    },
    "Bed": {
        "subcategories": ["Platform Bed", "Storage Bed", "Panel Bed"],
        "materials": ["Wood", "Engineered Wood", "Metal"],
        "styles": ["Contemporary", "Modern", "Minimalist"],
        "colors": ["Natural", "Brown", "White", "Black"],
    },
    "Table": {
        "subcategories": ["Dining Table", "Coffee Table", "Side Table"],
        "materials": ["Oak", "Walnut", "Wood", "Glass"],
        "styles": ["Scandinavian", "Modern", "Industrial"],
        "colors": ["Natural", "Brown", "Black", "White"],
    },
}


PRICE_RANGES = {
    "Sofa": (400, 1800),
    "Desk": (150, 900),
    "Chair": (80, 700),
    "Bed": (300, 1600),
    "Table": (120, 1000),
}


def generate_features(category):
    features = {
        "Sofa": [
            "Removable Cushions",
            "Stain Resistant",
            "Deep Seating",
            "Soft Fabric",
        ],
        "Desk": [
            "Cable Management",
            "Drawer",
            "Storage Shelf",
            "Scratch Resistant",
        ],
        "Chair": [
            "Adjustable Height",
            "Lumbar Support",
            "Padded Seat",
            "Ergonomic Design",
        ],
        "Bed": [
            "Storage",
            "Solid Wood",
            "Durable Frame",
            "Easy Assembly",
        ],
        "Table": [
            "Solid Wood",
            "Easy Assembly",
            "Scratch Resistant",
            "Durable Finish",
        ],
    }

    return random.sample(
        features[category],
        k=2,
    )


def generate_dimensions(category):
    if category == "Sofa":
        return {
            "width": random.randint(160, 240),
            "depth": random.randint(80, 100),
            "height": random.randint(75, 100),
            "unit": "cm",
        }

    if category == "Desk":
        return {
            "width": random.randint(100, 180),
            "depth": random.randint(50, 90),
            "height": random.randint(70, 80),
            "unit": "cm",
        }

    if category == "Chair":
        return {
            "width": random.randint(50, 75),
            "depth": random.randint(50, 75),
            "height": random.randint(80, 130),
            "unit": "cm",
        }

    if category == "Bed":
        return {
            "width": random.randint(140, 200),
            "depth": random.randint(190, 220),
            "height": random.randint(80, 120),
            "unit": "cm",
        }

    return {
        "width": random.randint(60, 160),
        "depth": random.randint(50, 140),
        "height": random.randint(40, 80),
        "unit": "cm",
    }


def generate_attributes(category):
    if category == "Sofa":
        return {
            "seating_capacity": random.choice([2, 3, 4, 5]),
            "upholstery": random.choice(
                ["Fabric", "Leather", "Velvet"]
            ),
        }

    if category == "Desk":
        return {
            "drawer_count": random.randint(0, 4),
            "cable_management": random.choice([True, False]),
        }

    if category == "Chair":
        return {
            "adjustable_height": random.choice([True, False]),
            "lumbar_support": random.choice([True, False]),
        }

    if category == "Bed":
        return {
            "mattress_size": random.choice(
                ["Queen", "King", "Twin"]
            ),
            "storage": random.choice([True, False]),
            "headboard_type": random.choice(
                ["Panel", "Upholstered", "Slatted"]
            ),
        }

    return {
        "seating_capacity": random.choice([2, 4, 6]),
        "shape": random.choice(
            ["Round", "Square", "Rectangular"]
        ),
    }


def generate_product(product_number):
    category = random.choice(list(CATEGORIES.keys()))
    category_data = CATEGORIES[category]

    subcategory = random.choice(
        category_data["subcategories"]
    )

    material = random.choice(
        category_data["materials"]
    )

    style = random.choice(
        category_data["styles"]
    )

    color = random.choice(
        category_data["colors"]
    )

    price_min, price_max = PRICE_RANGES[category]

    price = Decimal(
        str(
            round(
                random.uniform(
                    price_min,
                    price_max,
                ),
                2,
            )
        )
    )

    rating = round(
        random.uniform(3.5, 5.0),
        1,
    )

    review_count = random.randint(
        5,
        1000,
    )

    features = generate_features(category)

    dimensions = generate_dimensions(category)

    weight = round(
        random.uniform(5, 80),
        1,
    )

    name = (
        f"{style} {color} "
        f"{material} {subcategory}"
    )

    description = (
        f"A {style.lower()} {subcategory.lower()} "
        f"made from {material.lower()} in {color.lower()}. "
        f"Designed for comfortable and practical everyday use."
    )

    sku = f"{category.upper()}-{product_number:05d}"

    return Product(
        sku=sku,
        name=name,
        category=category,
        subcategory=subcategory,
        price=price,
        material=material,
        style=style,
        color=color,
        rating=rating,
        review_count=review_count,
        features=features,
        dimensions=dimensions,
        weight=weight,
        description=description,
        attributes=generate_attributes(category),
    )


def generate_products():
    db = SessionLocal()

    try:
        existing_count = db.query(Product).count()

        remaining = TARGET_PRODUCTS - existing_count

        if remaining <= 0:
            print(
                f"Database already contains "
                f"{existing_count} products."
            )
            return

        print(
            f"Existing products: {existing_count}"
        )

        print(
            f"Generating {remaining} products..."
        )

        products = []

        for i in range(
            existing_count + 1,
            TARGET_PRODUCTS + 1,
        ):
            products.append(
                generate_product(i)
            )

        db.bulk_save_objects(products)

        db.commit()

        print(
            f"Successfully generated "
            f"{remaining} products."
        )

        print(
            f"Total products: "
            f"{db.query(Product).count()}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    generate_products()