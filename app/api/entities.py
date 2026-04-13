from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app import models
from app.api.entity_schemas import (
    UserCreate, ProductCreate, OrderCreate, CustomerCreate, MessageCreate, EntityCreateResponse,
    UserResponse, ProductResponse, OrderResponse, CustomerResponse, MessageResponse
)
from app.services.sync_service import SyncService
from typing import List

router = APIRouter(prefix="/entities", tags=["Entities"])

@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.post("/users", response_model=EntityCreateResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    # 1. Save to main table
    user = models.User(name=data.name, email=data.email)
    db.add(user)
    db.commit()
    db.refresh(user)

    # 2. Sync to global search
    sync = SyncService(db)
    sync.on_create(
        entity_type="user",
        entity_id=user.id,
        title=user.name,
        description=user.email,
        extra_data={"email": user.email}
    )
    return {"id": user.id}

@router.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@router.post("/products", response_model=EntityCreateResponse)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    product = models.Product(name=data.name, description=data.description, price=data.price)
    db.add(product)
    db.commit()
    db.refresh(product)

    sync = SyncService(db)
    sync.on_create(
        entity_type="product",
        entity_id=product.id,
        title=product.name,
        description=product.description,
        extra_data={"price": product.price}
    )
    return {"id": product.id}

@router.get("/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@router.post("/orders", response_model=EntityCreateResponse)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    order = models.Order(order_number=data.order_number, status=data.status)
    db.add(order)
    db.commit()
    db.refresh(order)

    sync = SyncService(db)
    sync.on_create(
        entity_type="order",
        entity_id=order.id,
        title=f"Order {order.order_number}",
        description=order.status
    )
    return {"id": order.id}

@router.get("/customers", response_model=List[CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()

@router.post("/customers", response_model=EntityCreateResponse)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    customer = models.Customer(company_name=data.company_name, contact_email=data.contact_email)
    db.add(customer)
    db.commit()
    db.refresh(customer)

    sync = SyncService(db)
    sync.on_create(
        entity_type="customer",
        entity_id=customer.id,
        title=customer.company_name,
        description=customer.contact_email
    )
    return {"id": customer.id}

@router.get("/messages", response_model=List[MessageResponse])
def get_messages(db: Session = Depends(get_db)):
    return db.query(models.Message).all()

@router.post("/messages", response_model=EntityCreateResponse)
def create_message(data: MessageCreate, db: Session = Depends(get_db)):
    msg = models.Message(subject=data.subject, body=data.body)
    db.add(msg)
    db.commit()
    db.refresh(msg)

    sync = SyncService(db)
    sync.on_create(
        entity_type="message",
        entity_id=msg.id,
        title=msg.subject,
        description=msg.body
    )
    return {"id": msg.id}
