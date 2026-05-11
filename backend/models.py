import os

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=5,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Association table for many-to-many relationship between menu and categories
menu_categories = Table(
    "menu_categories",
    Base.metadata,
    Column("menu_id", Integer, ForeignKey("menu.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class CategoryModel(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationship with menu items
    menu_items = relationship("MenuModel", secondary=menu_categories, back_populates="categories")


class MenuModel(Base):
    __tablename__ = "menu"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=True)  # Legacy field, kept for backward compatibility
    image = Column(String, nullable=True)
    
    # Relationship with categories
    categories = relationship("CategoryModel", secondary=menu_categories, back_populates="menu_items")


class OrderModel(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime)


class OrderItemModel(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer)
    quantity = Column(Integer)


class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # "admin" or "user"
