from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.product import ProductResponse, ProductUpdate
from app.services.product_service import ProductService


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get("/search")
def search_products(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    results = ProductService.search_products(
        db=db,
        query=q,
        limit=limit,
    )

    return [
        {
            "product_id": product.product_id,
            "name": product.name,
            "keyword_score": float(keyword_score),
        }
        for product, keyword_score in results
    ]


@router.get("/semantic-search")
def semantic_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    results = ProductService.semantic_search(
        db=db,
        query=q,
        limit=limit,
    )

    return [
        {
            "product_id": product.product_id,
            "name": product.name,
            "distance": float(distance),
            "similarity": 1 - float(distance),
        }
        for product, distance in results
    ]


@router.get("/hybrid-search")
def hybrid_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    results = ProductService.hybrid_search(
        db=db,
        query=q,
        limit=limit,
    )

    return [
        {
            "product_id": item["product"].product_id,
            "sku": item["product"].sku,
            "name": item["product"].name,
            "category": item["product"].category,
            "subcategory": item["product"].subcategory,
            "price": float(item["product"].price),
            "material": item["product"].material,
            "style": item["product"].style,
            "color": item["product"].color,
            "rating": float(item["product"].rating),
            "review_count": item["product"].review_count,
            "description": item["product"].description,
            "dimensions": item["product"].dimensions,
            "weight": float(item["product"].weight),
            "features": item["product"].features,
            "score": item["score"],
            "score_breakdown": item["score_breakdown"],
        }
        for item in results
    ]


@router.get("/{product_id}/knowledge")
def get_product_knowledge(
    product_id: int,
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
):
    from app.services.embedding_service import embed_text
    from app.models.knowledge import KnowledgeChunk

    query_embedding = embed_text(q)
    distance = KnowledgeChunk.embedding.cosine_distance(query_embedding)

    chunks = (
        db.query(KnowledgeChunk, distance.label("distance"))
        .filter(
            KnowledgeChunk.product_id == product_id,
            KnowledgeChunk.embedding.is_not(None),
        )
        .order_by(distance)
        .limit(limit)
        .all()
    )

    return [
        {
            "chunk_id": chunk.chunk_id,
            "product_id": chunk.product_id,
            "document_type": chunk.document_type,
            "content": chunk.content,
            "similarity": round(1 - float(dist), 4),
        }
        for chunk, dist in chunks
    ]


@router.get("/", response_model=list[ProductResponse])
def get_products(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return ProductService.get_products(
        db,
        limit,
        offset,
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    updates: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = ProductService.update_product(
        db=db,
        product_id=product_id,
        updates=updates,
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = ProductService.get_product(
        db,
        product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product