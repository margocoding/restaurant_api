from app.db.database import Base, engine
from app.models.models import MenuItem, Order, OrderItem


def init_db():
    """Создать все таблицы в базе данных."""
    Base.metadata.create_all(bind=engine)
    
    db_session = None
    try:
        from app.db.database import SessionLocal
        db_session = SessionLocal()
        
        if db_session.query(MenuItem).count() == 0:
            sample_menu = [
                MenuItem(
                    name="Пицца Маргарита",
                    description="Сыр, томаты, базилик",
                    price=450.0,
                    category="Пицца",
                    image="https://example.com/margarita.jpg"
                ),
                MenuItem(
                    name="Пицца Пепперони",
                    description="Пепперони, сыр, томатный соус",
                    price=550.0,
                    category="Пицца",
                    image="https://example.com/pepperoni.jpg"
                ),
                MenuItem(
                    name="Паста Карбонара",
                    description="Бекон, сливки, пармезан, яичный желток",
                    price=480.0,
                    category="Паста",
                    image="https://example.com/carbonara.jpg"
                ),
                MenuItem(
                    name="Салат Цезарь",
                    description="Курица, салат ромэн, пармезан, сухарики",
                    price=390.0,
                    category="Салаты",
                    image="https://example.com/caesar.jpg"
                ),
                MenuItem(
                    name="Тирамису",
                    description="Классический итальянский десерт",
                    price=320.0,
                    category="Десерты",
                    image="https://example.com/tiramisu.jpg"
                ),
                MenuItem(
                    name="Лимонад",
                    description="Домашний лимонад с мятой",
                    price=180.0,
                    category="Напитки",
                    image="https://example.com/lemonade.jpg"
                ),
            ]
            db_session.add_all(sample_menu)
            db_session.commit()
            print("Sample menu items added successfully!")
        else:
            print("Menu items already exist.")
            
    except Exception as e:
        if db_session:
            db_session.rollback()
        print(f"Error initializing database: {e}")
    finally:
        if db_session:
            db_session.close()


if __name__ == "__main__":
    init_db()
