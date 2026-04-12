from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from app.repositories.search_repo import SearchRepository

class SyncService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SearchRepository(db)

    def on_create(self, entity_type: str, entity_id: int, title: str, description: Optional[str] = None, extra_data: Optional[Dict[str, Any]] = None):
        """Called by your entity services after a record is successfully created"""
        try:
            self.repo.upsert_search(entity_type, entity_id, title, description, extra_data)
        except Exception as e:
            # Optionally log, or push to a dead-letter queue if using async workers like Celery
            pass

    def on_update(self, entity_type: str, entity_id: int, title: str, description: Optional[str] = None, extra_data: Optional[Dict[str, Any]] = None):
        """Called by your entity services after a record is updated"""
        try:
            self.repo.upsert_search(entity_type, entity_id, title, description, extra_data)
        except Exception as e:
            # Handle error
            pass

    def on_delete(self, entity_type: str, entity_id: int):
        """Called by your entity services after a record is deleted"""
        try:
            self.repo.delete_search_entry(entity_type, entity_id)
        except Exception as e:
            # Handle error
            pass
