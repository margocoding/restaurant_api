from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.models import FavoriteModel, MenuModel, UserModel, get_db
from backend.schemas import Favorite, FavoriteCreate

router = APIRouter()


@router.get("/favorites", response_model=list[Favorite])
def get_favorites(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    """Get all items in the current user's favorites."""
    favorites = (
        db.query(FavoriteModel).filter(FavoriteModel.user_id == current_user.id).all()
    )
    return favorites


@router.post("/favorites", response_model=Favorite)
def add_to_favorites(
    item: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Add an item to favorites."""
    menu_item = db.query(MenuModel).filter(MenuModel.id == item.menu_item_id).first()
    if menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    existing_favorite = (
        db.query(FavoriteModel)
        .filter(
            FavoriteModel.user_id == current_user.id,
            FavoriteModel.menu_item_id == item.menu_item_id,
        )
        .first()
    )

    if existing_favorite:
        raise HTTPException(status_code=400, detail="Item already in favorites")

    new_favorite = FavoriteModel(
        user_id=current_user.id, menu_item_id=item.menu_item_id
    )
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return new_favorite


@router.delete("/favorites/{item_id}")
def remove_from_favorites(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Remove an item from favorites."""
    favorite = (
        db.query(FavoriteModel)
        .filter(FavoriteModel.id == item_id, FavoriteModel.user_id == current_user.id)
        .first()
    )

    if favorite is None:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(favorite)
    db.commit()
    return {"message": "Item removed from favorites"}
