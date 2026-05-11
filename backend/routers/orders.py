from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.models import MenuModel, OrderItemModel, OrderModel, get_db
from backend.schemas import Order, OrderCreate, OrderItem, OrderResponse, OrderStatusUpdate

router = APIRouter()


@router.post("/orders", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    if not order.customer_name or not order.phone or not order.address:
        raise HTTPException(status_code=400, detail="Customer name, phone and address are required")
    
    if not order.items or len(order.items) == 0:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")
    
    total = 0.0
    for item in order.items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        menu_item = db.query(MenuModel).filter(MenuModel.id == item.menu_item_id).first()
        
        if menu_item is None:
            raise HTTPException(status_code=400, detail=f"Menu item with id {item.menu_item_id} not found")
        
        total += menu_item.price * item.quantity
    
    new_order = OrderModel(
        customer_name=order.customer_name,
        phone=order.phone,
        address=order.address,
        total_amount=total,
        status="pending",
        created_at=datetime.now()
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    for item in order.items:
        order_item = OrderItemModel(
            order_id=new_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity
        )
        db.add(order_item)
    
    db.commit()
    
    order_items = []
    for item in order.items:
        order_items.append(OrderItem(menu_item_id=item.menu_item_id, quantity=item.quantity))
    
    return Order(
        id=new_order.id,
        customer_name=new_order.customer_name,
        phone=new_order.phone,
        address=new_order.address,
        items=order_items,
        total_amount=new_order.total_amount,
        status=new_order.status,
        created_at=new_order.created_at
    )


@router.get("/orders", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(OrderModel).order_by(OrderModel.created_at.desc()).all()
    
    result = []
    for order in orders:
        result.append(OrderResponse(
            id=order.id,
            customer_name=order.customer_name,
            phone=order.phone,
            address=order.address,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at
        ))
    return result


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, status_update: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    valid_statuses = ["pending", "confirmed", "preparing", "ready", "delivered", "cancelled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    
    return OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        phone=order.phone,
        address=order.address,
        total_amount=order.total_amount,
        status=order.status,
        created_at=order.created_at
    )
