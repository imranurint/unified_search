from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: int

class OrderCreate(BaseModel):
    order_number: str
    status: str = "pending"

class CustomerCreate(BaseModel):
    company_name: str
    contact_email: EmailStr

class MessageCreate(BaseModel):
    subject: str
    body: str

class EntityCreateResponse(BaseModel):
    id: int
    status: str = "created_and_synced"

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    class Config:
        from_attributes = True

class CustomerResponse(BaseModel):
    id: int
    company_name: str
    contact_email: str
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    subject: str
    body: str
    class Config:
        from_attributes = True
