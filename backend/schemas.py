import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Category(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class MenuItem(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: Optional[str] = None
    image: Optional[str] = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    price: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=100)
    image: Optional[str] = None
    category_ids: Optional[List[int]] = None

    @field_validator("image")
    @classmethod
    def validate_image_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Simple URL validation
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        if not url_pattern.match(v):
            raise ValueError("Invalid URL format for image")
        return v


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    image: Optional[str] = None
    category_ids: Optional[List[int]] = None

    @field_validator("image")
    @classmethod
    def validate_image_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        url_pattern = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        if not url_pattern.match(v):
            raise ValueError("Invalid URL format for image")
        return v


class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=10, max_length=20)
    address: str = Field(..., min_length=1, max_length=500)
    items: List[OrderItem] = Field(..., min_length=1)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        # Check if it contains only digits and starts with + or digits
        if not re.match(r"^\+?\d{10,15}$", cleaned):
            raise ValueError("Phone number must be in valid format (10-15 digits)")
        return v


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=50)


class Order(BaseModel):
    id: int
    customer_name: str
    phone: str
    address: str
    items: List[OrderItem]
    total_amount: float
    status: str
    created_at: datetime


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    phone: str
    address: str
    total_amount: float
    status: str
    created_at: datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    role: Optional[str] = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class CartItem(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    id: int
    menu_item_id: int
    quantity: int


class CartItemCreate(BaseModel):
    menu_item_id: int = Field(..., gt=0)
    quantity: int = Field(default=1, gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class Favorite(BaseModel):
    id: int
    menu_item_id: int


class FavoriteCreate(BaseModel):
    menu_item_id: int = Field(..., gt=0)


class OrderFromCart(BaseModel):
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
