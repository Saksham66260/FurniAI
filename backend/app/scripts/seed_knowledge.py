from app.db.database import SessionLocal
from app.models.knowledge import KnowledgeChunk
from app.services.embedding_service import embed_text


KNOWLEDGE_DATA = [
    {
        "product_id": 1174,
        "document_type": "assembly_manual",
        "content": (
            "The Industrial White Oak Computer Desk requires assembly. "
            "The desk includes a storage shelf and drawers. "
            "Assembly should be performed on a stable, level surface."
        ),
    },
    {
        "product_id": 1174,
        "document_type": "care_guide",
        "content": (
            "Clean the Industrial White Oak Computer Desk with a soft, "
            "slightly damp cloth. Avoid abrasive cleaners and excessive moisture."
        ),
    },
    {
        "product_id": 1912,
        "document_type": "assembly_manual",
        "content": (
            "The Industrial Black Oak Computer Desk requires assembly. "
            "Follow the included assembly instructions and place the desk "
            "on a stable, level surface."
        ),
    },
    {
        "product_id": 1912,
        "document_type": "care_guide",
        "content": (
            "Clean the Industrial Black Oak Computer Desk with a soft cloth. "
            "Avoid abrasive cleaning products and excessive moisture."
        ),
    },
]


def seed_knowledge():
    db = SessionLocal()

    try:
        for item in KNOWLEDGE_DATA:
            embedding = embed_text(item["content"])

            chunk = KnowledgeChunk(
                product_id=item["product_id"],
                document_type=item["document_type"],
                content=item["content"],
                embedding=embedding,
            )

            db.add(chunk)

        db.commit()

        print(f"Inserted {len(KNOWLEDGE_DATA)} knowledge chunks.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_knowledge()