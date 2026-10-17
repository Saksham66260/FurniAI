from pydantic import BaseModel


class OrderCreate(BaseModel):
    user_id: int


class OrderItemResponse(BaseModel):
    order_item_id: int
    product_id: int
    quantity: int
    unit_price: float


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: float
    items: list[OrderItemResponse]