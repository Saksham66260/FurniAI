from typing import Optional, Literal

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.services.order_service import OrderService
from app.models.knowledge import KnowledgeChunk
from app.services.embedding_service import embed_text
from app.db.database import SessionLocal
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.warehouse import Warehouse
from app.services.product_service import ProductService


# ============================================================
# TOOL INPUT SCHEMAS
# ============================================================

class SearchProductsInput(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=200,
        description="Natural-language description of the furniture the user wants."
    )

    max_price: Optional[float] = Field(
        default=None,
        gt=0,
        description="Maximum acceptable product price."
    )

    category: Optional[
        Literal["Bed", "Chair", "Desk", "Sofa", "Table"]
    ] = Field(
        default=None,
        description="Furniture category."
    )


class CompareProductsInput(BaseModel):
    product_ids: list[int] = Field(
        min_length=1,
        max_length=10,
        description="Product IDs to compare."
    )


class InventoryInput(BaseModel):
    product_id: int = Field(
        gt=0,
        description="Product ID to check."
    )

    quantity: int = Field(
        default=1,
        gt=0,
        description="Quantity required."
    )


class ProductKnowledgeInput(BaseModel):
    product_id: int = Field(
        gt=0,
        description="Product ID whose documentation should be searched."
    )

    question: str = Field(
        min_length=1,
        max_length=500,
        description="Question about the product documentation."
    )

class CheckoutInput(BaseModel):
    confirm: bool = Field(
        default=True,
        description="Indicates that the user intends to proceed with checkout."
    )
# ============================================================
# SEARCH PRODUCTS
# ============================================================

@tool(args_schema=SearchProductsInput)
def search_products(
    query: str,
    max_price: Optional[float] = None,
    category: Optional[str] = None,
) -> list[dict]:
    """Search FurniAI products using hybrid lexical and semantic search with deterministic backend ranking."""

    db: Session = SessionLocal()

    try:
        results = ProductService.hybrid_search(
            db=db,
            query=query,
            limit=20,
        )

        output = []

        for result in results:
            product = result["product"]

            if max_price is not None and float(product.price) > max_price:
                continue

            if (
                category is not None
                and product.category.lower() != category.lower()
            ):
                continue

            output.append({
                "product_id": product.product_id,
                "name": product.name,
                "price": float(product.price),
                "category": product.category,
                "score": float(result["score"]),
                "score_breakdown": result["score_breakdown"],
            })

        return output

    finally:
        db.close()


# ============================================================
# COMPARE PRODUCTS
# ============================================================

@tool(args_schema=CompareProductsInput)
def compare_products(
    product_ids: list[int],
) -> list[dict]:
    """Return authoritative product specifications for comparing FurniAI products."""

    db: Session = SessionLocal()

    try:
        products = (
            db.query(Product)
            .filter(Product.product_id.in_(product_ids))
            .all()
        )

        products_by_id = {
            product.product_id: product
            for product in products
        }

        output = []

        for product_id in product_ids:
            product = products_by_id.get(product_id)

            if product is None:
                continue

            output.append({
                "product_id": product.product_id,
                "name": product.name,
                "sku": product.sku,
                "category": product.category,
                "subcategory": product.subcategory,
                "price": float(product.price),
                "material": product.material,
                "style": product.style,
                "color": product.color,
                "rating": float(product.rating),
                "review_count": product.review_count,
                "features": product.features,
                "dimensions": product.dimensions,
                "weight": float(product.weight),
                "description": product.description,
                "attributes": product.attributes,
            })

        return output

    finally:
        db.close()


# ============================================================
# INVENTORY
# ============================================================

@tool(args_schema=InventoryInput)
def check_inventory_and_delivery(
    product_id: int,
    quantity: int = 1,
) -> list[dict]:
    """Check current PostgreSQL inventory and warehouse information for a product."""

    db: Session = SessionLocal()

    try:
        rows = (
            db.query(Inventory, Warehouse)
            .join(
                Warehouse,
                Inventory.warehouse_id == Warehouse.warehouse_id,
            )
            .filter(
                Inventory.product_id == product_id,
                Inventory.quantity >= quantity,
            )
            .all()
        )

        output = []

        for inventory, warehouse in rows:
            output.append({
                "product_id": product_id,
                "warehouse_id": warehouse.warehouse_id,
                "warehouse_name": warehouse.name,
                "warehouse_location": warehouse.location,
                "available_quantity": inventory.quantity,
                "requested_quantity": quantity,
            })

        return output

    finally:
        db.close()


# ============================================================
# RAG / PRODUCT KNOWLEDGE
# ============================================================

@tool(args_schema=ProductKnowledgeInput)
def get_product_knowledge(
    product_id: int,
    question: str,
) -> list[dict]:
    """Retrieve grounded product knowledge from FurniAI documentation."""

    db: Session = SessionLocal()

    try:
        query_embedding = embed_text(question)

        distance = KnowledgeChunk.embedding.cosine_distance(
            query_embedding
        )

        chunks = (
            db.query(
                KnowledgeChunk,
                distance.label("distance"),
            )
            .filter(
                KnowledgeChunk.product_id == product_id,
                KnowledgeChunk.embedding.is_not(None),
            )
            .order_by(distance)
            .limit(5)
            .all()
        )

        return [
            {
                "product_id": chunk.product_id,
                "document_type": chunk.document_type,
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "similarity": 1 - float(dist),
            }
            for chunk, dist in chunks
        ]

    finally:
        db.close()
@tool(args_schema=CheckoutInput)
def checkout(confirm: bool = True) -> dict:
    """
    Prepare a checkout request.

    Actual execution is controlled by the LangGraph human-approval gate.
    The authenticated user ID and idempotency key are supplied by the
    application layer, not by the LLM.
    """

    if not confirm:
        return {
            "success": False,
            "status": "CANCELLED",
            "message": "Checkout was not confirmed.",
        }

    return {
        "success": False,
        "status": "CHECKOUT_READY",
        "message": (
            "Checkout is ready. Human approval is required before "
            "the order can be created."
        ),
    }