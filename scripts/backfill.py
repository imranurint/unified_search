import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Base

def build_search_vector(title: str, description: str):
    # This is a Python stub, actually you would use raw SQL for performance 
    # and to ensure correct tsvector parsing. The example does the heavy lifting in DB.
    pass

def backfill_data(db: Session):
    print("Starting backfill migration...")
    
    # Empty current table
    db.execute(text("TRUNCATE TABLE global_search RESTART IDENTITY"))

    # For a real scale, you'd use batch inserts or server-side cursors.
    print("Backfilling Users...")
    db.execute(text("""
        INSERT INTO global_search (entity_type, entity_id, title, description, extra_data)
        SELECT 'user', id, name, email, '{"type": "user"}'
        FROM users;
    """))

    print("Backfilling Products...")
    db.execute(text("""
        INSERT INTO global_search (entity_type, entity_id, title, description, extra_data)
        SELECT 'product', id, name, description, '{"type": "product"}'
        FROM products;
    """))
    
    # Extend for other tables here...
    
    db.commit()
    print("Backfill completed successfully.")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine) # Ensure tables exist
    
    db = SessionLocal()
    try:
        backfill_data(db)
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
    finally:
        db.close()
