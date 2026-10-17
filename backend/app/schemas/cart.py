from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(gt=0)

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int


class CartResponse(BaseModel):
    cart_id: int
    user_id: int
    items: list[CartItemResponse]

class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)