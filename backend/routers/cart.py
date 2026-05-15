from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.models import CartItemModel, MenuModel, UserModel, get_db
from backend.schemas import CartItemCreate, CartItemResponse, CartItemUpdate

router = APIRouter()


@router.get("/cart", response_model=list[CartItemResponse])
def get_cart(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    """Get all items in the current user's cart."""
    cart_items = (
        db.query(CartItemModel).filter(CartItemModel.user_id == current_user.id).all()
    )
    return cart_items


@router.post("/cart", response_model=CartItemResponse)
def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Add an item to the cart or update quantity if already exists."""
    menu_item = db.query(MenuModel).filter(MenuModel.id == item.menu_item_id).first()
    if menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    existing_item = (
        db.query(CartItemModel)
        .filter(
            CartItemModel.user_id == current_user.id,
            CartItemModel.menu_item_id == item.menu_item_id,
        )
        .first()
    )

    if existing_item:
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    new_item = CartItemModel(
        user_id=current_user.id, menu_item_id=item.menu_item_id, quantity=item.quantity
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.put("/cart/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Update quantity of a cart item."""
    cart_item = (
        db.query(CartItemModel)
        .filter(CartItemModel.id == item_id, CartItemModel.user_id == current_user.id)
        .first()
    )

    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart_item.quantity = item_update.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.delete("/cart/{item_id}")
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Remove an item from the cart."""
    cart_item = (
        db.query(CartItemModel)
        .filter(CartItemModel.id == item_id, CartItemModel.user_id == current_user.id)
        .first()
    )

    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("/cart")
def clear_cart(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    """Clear all items from the cart."""
    db.query(CartItemModel).filter(CartItemModel.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}
