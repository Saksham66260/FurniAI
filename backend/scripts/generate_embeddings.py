from app.db.database import SessionLocal
from app.models.product import Product
from app.services.embedding_service import model


def product_text(product: Product) -> str:
    return " ".join(
        filter(
            None,
            [
                product.name,
                product.category,
                product.subcategory,
                product.material,
                product.style,
                product.color,
                " ".join(product.features or []),
                product.description,
            ],
        )
    )


def main():
    db = SessionLocal()

    try:
        products = db.query(Product).all()

        texts = [product_text(product) for product in products]

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=True,
        )

        for product, embedding in zip(products, embeddings):
            product.embedding = embedding.tolist()

        db.commit()

        print(f"Generated embeddings for {len(products)} products")

    finally:
        db.close()


if __name__ == "__main__":
    main()