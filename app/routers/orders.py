from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import Order, OrderItem, MenuItem, OrderStatusEnum
from app.schemas.schemas import OrderCreate, OrderResponse, OrderStatusUpdate

router = APIRouter()


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """
    Создать новый заказ.
    
    Тело запроса:
    {
      "items": [
        {"menu_item_id": 1, "quantity": 2},
        {"menu_item_id": 3, "quantity": 1}
      ]
    }
    """
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ должен содержать хотя бы одно блюдо"
        )
    
    total_price = 0.0
    order_items = []
    
    for item in order_data.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Блюдо с id {item.menu_item_id} не найдено"
            )
        
        item_price = menu_item.price * item.quantity
        total_price += item_price
        
        order_item = OrderItem(
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price=menu_item.price
        )
        order_items.append(order_item)
    
    order = Order(total_price=total_price, items=order_items)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(db: Session = Depends(get_db)):
    """
    Получить список всех заказов.
    """
    orders = db.query(Order).all()
    return orders


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить статус заказа.
    
    Возможные статусы: pending, confirmed, cooking, ready, delivered, cancelled
    
    Тело запроса:
    {
      "status": "confirmed"
    }
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с id {order_id} не найден"
        )
    
    try:
        order.status = OrderStatusEnum(status_data.status)
    except ValueError:
        valid_statuses = [s.value for s in OrderStatusEnum]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невалидный статус. Допустимые значения: {valid_statuses}"
        )
    
    db.commit()
    db.refresh(order)
    
    return order
