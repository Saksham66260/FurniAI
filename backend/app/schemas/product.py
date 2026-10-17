from typing import Any

from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    sku: str
    name: str
    category: str
    subcategory: str
    price: float
    material: str
    style: str
    color: str
    rating: float
    review_count: int
    features: list[str]
    dimensions: dict[str, Any]
    weight: float
    description: str
    attributes: dict[str, Any]

class ProductUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    category: str | None = None
    subcategory: str | None = None
    price: float | None = None
    material: str | None = None
    style: str | None = None
    color: str | None = None
    rating: float | None = None
    review_count: int | None = None
    features: list[str] | None = None
    dimensions: dict[str, Any] | None = None
    weight: float | None = None
    description: str | None = None
    attributes: dict[str, Any] | None = None