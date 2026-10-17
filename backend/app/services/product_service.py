import json
import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.cache.redis import redis_client
from app.models.product import Product
from app.schemas.product import ProductResponse, ProductUpdate
from app.services.embedding_service import embed_text


logger = logging.getLogger(__name__)


class ProductService:

    @staticmethod
    def hybrid_search(
        db: Session,
        query: str,
        limit: int = 20,
    ):
        query_embedding = embed_text(query)
        search_query = func.plainto_tsquery("english", query)

        distance = Product.embedding.cosine_distance(query_embedding)

        keyword_score = func.ts_rank(
            Product.search_vector,
            search_query,
        )

        # Semantic search candidates
        semantic_results = (
            db.query(
                Product,
                distance.label("distance"),
            )
            .filter(Product.embedding.is_not(None))
            .order_by(distance)
            .limit(50)
            .all()
        )

        # Keyword search candidates
        keyword_results = (
            db.query(
                Product,
                keyword_score.label("keyword_score"),
            )
            .filter(
                Product.search_vector.op("@@")(search_query)
            )
            .order_by(keyword_score.desc())
            .limit(50)
            .all()
        )

        semantic_map = {
            product.product_id: 1 - float(dist)
            for product, dist in semantic_results
        }

        keyword_map = {
            product.product_id: float(score)
            for product, score in keyword_results
        }

        # Merge candidates
        candidates = {
            product.product_id: product
            for product, _ in semantic_results
        }

        for product, _ in keyword_results:
            candidates[product.product_id] = product

        if not candidates:
            return []

        semantic_values = list(semantic_map.values())
        keyword_values = list(keyword_map.values())

        def normalize(value, values):
            if not values:
                return 0.0

            min_value = min(values)
            max_value = max(values)

            if max_value == min_value:
                return 1.0

            return (value - min_value) / (
                max_value - min_value
            )

        prices = [
            float(product.price)
            for product in candidates.values()
        ]

        min_price = min(prices)
        max_price = max(prices)

        results = []

        for product_id, product in candidates.items():

            semantic = normalize(
                semantic_map.get(product_id, 0.0),
                semantic_values,
            )

            keyword = normalize(
                keyword_map.get(product_id, 0.0),
                keyword_values,
            )

            rating = float(product.rating) / 5.0

            if max_price == min_price:
                price = 1.0
            else:
                price = (
                    max_price - float(product.price)
                ) / (
                    max_price - min_price
                )

            score = (
                0.50 * semantic
                + 0.20 * keyword
                + 0.15 * rating
                + 0.15 * price
            )

            results.append(
                {
                    "product": product,
                    "score": score,
                    "score_breakdown": {
                        "semantic": semantic,
                        "keyword": keyword,
                        "rating": rating,
                        "price": price,
                    },
                }
            )

        results.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return results[:limit]

    @staticmethod
    def semantic_search(
        db: Session,
        query: str,
        limit: int = 20,
    ):
        query_embedding = embed_text(query)

        distance = Product.embedding.cosine_distance(
            query_embedding
        )

        return (
            db.query(
                Product,
                distance.label("distance"),
            )
            .filter(Product.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_product(
        db: Session,
        product_id: int,
    ) -> ProductResponse | None:

        cache_key = f"product:{product_id}"

        # 1. Check Redis
        cached_product = redis_client.get(cache_key)

        if cached_product:
            logger.info(
                "Redis cache HIT: %s",
                cache_key,
            )

            return ProductResponse(
                **json.loads(cached_product)
            )

        logger.info(
            "Redis cache MISS: %s",
            cache_key,
        )

        # 2. Cache miss → PostgreSQL
        product = (
            db.query(Product)
            .filter(Product.product_id == product_id)
            .first()
        )

        if product is None:
            logger.info(
                "Product not found: %s",
                product_id,
            )

            return None

        # 3. Convert database object → API representation
        product_response = ProductResponse.model_validate(product)

        # 4. Store product in Redis for 15 minutes
        redis_client.set(
            cache_key,
            json.dumps(product_response.model_dump()),
            ex=900,
        )

        logger.info(
            "Product cached: %s | TTL=900 seconds",
            cache_key,
        )

        # 5. Return product
        return product_response

    @staticmethod
    def get_products(
        db: Session,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        return (
            db.query(Product)
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def search_products(
        db: Session,
        query: str,
        limit: int = 20,
    ):
        search_query = func.plainto_tsquery(
            "english",
            query,
        )

        return (
            db.query(
                Product,
                func.ts_rank(
                    Product.search_vector,
                    search_query,
                ).label("keyword_score"),
            )
            .filter(
                Product.search_vector.op("@@")(
                    search_query
                )
            )
            .order_by(
                func.ts_rank(
                    Product.search_vector,
                    search_query,
                ).desc()
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        updates: ProductUpdate,
    ) -> ProductResponse | None:

        # 1. Find product in PostgreSQL
        product = (
            db.query(Product)
            .filter(Product.product_id == product_id)
            .first()
        )

        if product is None:
            return None

        # 2. Apply only fields supplied in the request
        update_data = updates.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(product, field, value)

        # 3. Commit authoritative database update
        db.commit()

        # 4. Refresh SQLAlchemy object with database state
        db.refresh(product)

        # 5. Invalidate Redis cache
        cache_key = f"product:{product_id}"

        deleted = redis_client.delete(cache_key)

        logger.info(
            "Product updated: %s | Redis cache invalidated: %s",
            product_id,
            bool(deleted),
        )

        # 6. Return fresh product
        return ProductResponse.model_validate(product)