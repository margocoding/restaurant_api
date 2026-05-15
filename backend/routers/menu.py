from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth import require_admin
from backend.models import CategoryModel, MenuModel, UserModel, get_db
from backend.schemas import (
    Category,
    CategoryCreate,
    CategoryUpdate,
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
)

router = APIRouter()


# ============== Categories CRUD ==============


@router.get("/categories", response_model=list[Category])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories."""
    categories = db.query(CategoryModel).all()
    return categories


@router.get("/categories/{category_id}", response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID."""
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/categories", response_model=Category)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(require_admin),
):
    """Create a new category (admin only)."""
    # Check if category with same name exists
    existing = (
        db.query(CategoryModel).filter(CategoryModel.name == category.name).first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Category with this name already exists"
        )

    db_category = CategoryModel(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/categories/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(require_admin),
):
    """Update a category (admin only)."""
    db_category = (
        db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    )
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check for duplicate name if updating name
    if category_update.name is not None:
        existing = (
            db.query(CategoryModel)
            .filter(
                CategoryModel.name == category_update.name,
                CategoryModel.id != category_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Category with this name already exists"
            )
        db_category.name = category_update.name

    if category_update.description is not None:
        db_category.description = category_update.description

    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(require_admin),
):
    """Delete a category (admin only)."""
    db_category = (
        db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    )
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}


# ============== Menu Items CRUD ==============


@router.get("/menu", response_model=list[MenuItem])
def get_menu(category: str = None, search: str = None, db: Session = Depends(get_db)):
    """
    Get menu items with optional filtering.

    - **category**: Filter by category name
    - **search**: Search in item name and description
    """
    query = db.query(MenuModel)

    # Filter by category
    if category:
        query = query.filter(MenuModel.category == category)

    # Search by name or description
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (MenuModel.name.ilike(search_term))
            | (MenuModel.description.ilike(search_term))
        )

    items = query.all()

    if len(items) == 0:
        default_items = [
            MenuModel(
                name="Пицца Маргарита",
                description="Сыр, томаты, базилик",
                price=450.0,
                category="Пицца",
                image="https://example.com/margarita.jpg",
            ),
            MenuModel(
                name="Пицца Пепперони",
                description="Пепперони, сыр, томатный соус",
                price=550.0,
                category="Пицца",
                image="https://example.com/pepperoni.jpg",
            ),
            MenuModel(
                name="Борщ",
                description="Традиционный украинский борщ со сметаной",
                price=320.0,
                category="Супы",
                image="https://example.com/borscht.jpg",
            ),
            MenuModel(
                name="Цезарь с курицей",
                description="Салат с курицей, пармезаном и сухариками",
                price=380.0,
                category="Салаты",
                image="https://example.com/caesar.jpg",
            ),
            MenuModel(
                name="Паста Карбонара",
                description="Спагетти с беконом, яйцом и пармезаном",
                price=420.0,
                category="Паста",
                image="https://example.com/carbonara.jpg",
            ),
            MenuModel(
                name="Тирамису",
                description="Классический итальянский десерт",
                price=290.0,
                category="Десерты",
                image="https://example.com/tiramisu.jpg",
            ),
            MenuModel(
                name="Чизкейк",
                description="Нежный творожный чизкейк",
                price=310.0,
                category="Десерты",
                image="https://example.com/cheesecake.jpg",
            ),
            MenuModel(
                name="Лимонад домашний",
                description="Освежающий лимонад с мятой",
                price=150.0,
                category="Напитки",
                image="https://example.com/lemonade.jpg",
            ),
        ]

        for item in default_items:
            db.add(item)
        db.commit()

        items = db.query(MenuModel).all()

    return items


@router.get("/menu/{item_id}", response_model=MenuItem)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific menu item by ID."""
    item = db.query(MenuModel).filter(MenuModel.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


@router.post("/menu", response_model=MenuItem)
def create_menu_item(
    item: MenuItemCreate,
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(require_admin),
):
    """Create a new menu item (admin only)."""
    db_item = MenuModel(
        name=item.name,
        description=item.description,
        price=item.price,
        category=item.category,
        image=item.image,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # Associate with categories if provided
    if item.category_ids:
        categories = (
            db.query(CategoryModel)
            .filter(CategoryModel.id.in_(item.category_ids))
            .all()
        )
        db_item.categories = categories
        db.commit()
        db.refresh(db_item)

    return db_item


@router.put("/menu/{item_id}", response_model=MenuItem)
def update_menu_item(
    item_id: int,
    item_update: MenuItemUpdate,
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(require_admin),
):
    """Update a menu item (admin only)."""
    db_item = db.query(MenuModel).filter(MenuModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    if item_update.name is not None:
        db_item.name = item_update.name
    if item_update.description is not None:
        db_item.description = item_update.description
    if item_update.price is not None:
        db_item.price = item_update.price
    if item_update.category is not None:
        db_item.category = item_update.category
    if item_update.image is not None:
        db_item.image = item_update.image

    # Update category associations if provided
    if item_update.category_ids is not None:
        categories = (
            db.query(CategoryModel)
            .filter(CategoryModel.id.in_(item_update.category_ids))
            .all()
        )
        db_item.categories = categories

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/menu/{item_id}")
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(require_admin),
):
    """Delete a menu item (admin only)."""
    db_item = db.query(MenuModel).filter(MenuModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(db_item)
    db.commit()
    return {"message": "Menu item deleted successfully"}
