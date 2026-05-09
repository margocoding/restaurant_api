from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: Optional[str] = "Пицца"
    image: Optional[str] = None


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemResponse(MenuItemBase):
    id: int

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(1, ge=1)


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    status: str
    total_price: float
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str
