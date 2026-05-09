from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import MenuItem
from app.schemas.schemas import MenuItemResponse

router = APIRouter()


@router.get("/menu", response_model=List[MenuItemResponse])
async def get_menu(db: Session = Depends(get_db)):
    """
    Получить список всех блюд меню.
    
    Возвращает:
    [
      {
        "id": 1,
        "name": "Пицца Маргарита",
        "description": "Сыр, томаты, базилик",
        "price": 450,
        "category": "Пицца",
        "image": "url"
      }
    ]
    """
    menu_items = db.query(MenuItem).all()
    return menu_items
