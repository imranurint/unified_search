from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from sqlalchemy.types import TypeDecorator
import json
from app.database import Base

# Simple JSON decorator for SQLite since it lacks native JSONB
class SQLiteJSON(TypeDecorator):
    impl = Text
    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None
    def process_result_value(self, value, dialect):
        return json.loads(value) if value is not None else None

class GlobalSearch(Base):
    __tablename__ = 'global_search'

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    extra_data = Column(SQLiteJSON) # Using custom decorator for SQLite
    
    # We remove search_vector as SQLite uses external FTS5 virtual tables for indexing

    __table_args__ = (
        UniqueConstraint('entity_type', 'entity_id', name='uq_entity_type_id'),
    )

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255))

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    price = Column(Integer)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(255))
    status = Column(String(50))
    
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255))
    contact_email = Column(String(255))
    
class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255))
    body = Column(Text)
