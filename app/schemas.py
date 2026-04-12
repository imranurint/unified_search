from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class SearchQuery(BaseModel):
    q: str
    type: Optional[str] = None
    limit: int = 20
    offset: int = 0

class SearchResultItem(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    title: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    rank: float
    headline: Optional[str]

    class Config:
        orm_mode = True

class HydratedSearchResult(BaseModel):
    metadata: Dict[str, Any]
    items: List[Dict[str, Any]]  # The hydrated entities

class SyncPayload(BaseModel):
    entity_type: str
    entity_id: int
    title: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
