from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class CategoryEnum(str, enum.Enum):
    pizza = "Пицца"
    pasta = "Паста"
    salad = "Салаты"
    soup = "Супы"
    dessert = "Десерты"
    drink = "Напитки"


class OrderStatusEnum(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cooking = "cooking"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    category = Column(String, default=CategoryEnum.pizza.value)
    image = Column(String, nullable=True)

    order_items = relationship("OrderItem", back_populates="menu_item")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(SQLEnum(OrderStatusEnum), default=OrderStatusEnum.pending)
    total_price = Column(Float, default=0.0)

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    menu_item_id = Column(Integer, index=True)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")
