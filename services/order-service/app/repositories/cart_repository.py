from uuid import UUID
from typing import Optional, List
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cart import Cart, CartItem
from decimal import Decimal


class CartRepository:
    """Repository for cart database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_cart(self, customer_id: UUID) -> Cart:
        """Get existing cart or create a new one for the customer."""
        result = await self.db.execute(
            select(Cart).where(Cart.customer_id == customer_id)
        )
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(customer_id=customer_id)
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart)

        return cart

    async def get_cart(self, customer_id: UUID) -> Optional[Cart]:
        """Get a customer's cart."""
        result = await self.db.execute(
            select(Cart).where(Cart.customer_id == customer_id)
        )
        return result.scalar_one_or_none()

    async def add_item(
        self,
        cart_id: UUID,
        product_id: UUID,
        product_name: str,
        quantity: int,
        unit_price: Decimal
    ) -> CartItem:
        """Add an item to the cart."""
        # Check if item already exists in cart
        result = await self.db.execute(
            select(CartItem).where(
                and_(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == product_id
                )
            )
        )
        existing_item = result.scalar_one_or_none()

        if existing_item:
            # Update quantity
            existing_item.quantity += quantity
            existing_item.subtotal = existing_item.quantity * unit_price
            await self.db.commit()
            await self.db.refresh(existing_item)
            return existing_item
        else:
            # Create new item
            item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=quantity * unit_price
            )
            self.db.add(item)
            await self.db.commit()
            await self.db.refresh(item)
            return item

    async def update_item_quantity(
        self,
        cart_id: UUID,
        product_id: UUID,
        quantity: int
    ) -> Optional[CartItem]:
        """Update the quantity of a cart item."""
        result = await self.db.execute(
            select(CartItem).where(
                and_(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == product_id
                )
            )
        )
        item = result.scalar_one_or_none()

        if not item:
            return None

        if quantity <= 0:
            await self.db.delete(item)
            await self.db.commit()
            return None
        else:
            item.quantity = quantity
            item.subtotal = quantity * item.unit_price
            await self.db.commit()
            await self.db.refresh(item)
            return item

    async def remove_item(self, cart_id: UUID, product_id: UUID) -> bool:
        """Remove an item from the cart."""
        result = await self.db.execute(
            delete(CartItem).where(
                and_(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == product_id
                )
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def clear_cart(self, cart_id: UUID) -> bool:
        """Clear all items from a cart."""
        result = await self.db.execute(
            delete(CartItem).where(CartItem.cart_id == cart_id)
        )
        await self.db.commit()
        return True

    async def get_cart_total(self, cart_id: UUID) -> Decimal:
        """Calculate the total amount of the cart."""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.sum(CartItem.subtotal)).where(CartItem.cart_id == cart_id)
        )
        total = result.scalar()
        return Decimal(total) if total else Decimal("0.00")
