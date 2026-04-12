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
