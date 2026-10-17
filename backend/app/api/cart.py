from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
    CartResponse,
)
from app.services.cart_service import CartService
from app.models.user import User


router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/{user_id}", response_model=CartResponse)
def get_cart(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    cart = CartService.get_cart(db, user_id)

    if cart is None:
        raise HTTPException(
            status_code=404,
            detail="Cart not found",
        )

    return {
        "cart_id": cart.id,
        "user_id": cart.user_id,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
            }
            for item in cart.items
        ],
    }
@router.post("/items", status_code=201)
def add_cart_item(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == item_data.user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    try:
        cart_item = CartService.add_item(
            db=db,
            user_id=item_data.user_id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )

        return {
            "id": cart_item.id,
            "cart_id": cart_item.cart_id,
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

@router.patch("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
):
    cart_item = CartService.update_item_quantity(
        db=db,
        item_id=item_id,
        quantity=item_data.quantity,
    )

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    return {
        "id": cart_item.id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity,
    }