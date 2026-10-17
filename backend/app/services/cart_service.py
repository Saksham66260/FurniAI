from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product


class CartService:

    @staticmethod
    def get_or_create_cart(
        db: Session,
        user_id: int,
    ) -> Cart:
        cart = (
            db.query(Cart)
            .filter(Cart.user_id == user_id)
            .first()
        )

        if cart is None:
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.flush()

        return cart

    @staticmethod
    def add_item(
        db: Session,
        user_id: int,
        product_id: int,
        quantity: int,
    ) -> CartItem:

        product = (
            db.query(Product)
            .filter(Product.product_id == product_id)
            .first()
        )

        if product is None:
            raise ValueError("Product not found")

        cart = CartService.get_or_create_cart(
            db=db,
            user_id=user_id,
        )

        cart_item = (
            db.query(CartItem)
            .filter(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id,
            )
            .first()
        )

        if cart_item is None:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
            )

            db.add(cart_item)

        else:
            cart_item.quantity += quantity

        db.commit()
        db.refresh(cart_item)

        return cart_item

    @staticmethod
    def get_cart(
        db: Session,
        user_id: int,
    ) -> Cart | None:

        return (
            db.query(Cart)
            .filter(Cart.user_id == user_id)
            .first()
        )

    @staticmethod
    def update_item_quantity(
        db: Session,
        item_id: int,
        quantity: int,
    ) -> CartItem | None:

        cart_item = (
            db.query(CartItem)
            .filter(CartItem.id == item_id)
            .first()
        )

        if cart_item is None:
            return None

        cart_item.quantity = quantity

        db.commit()
        db.refresh(cart_item)

        return cart_item