from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.services.search_service import SearchService
from app.services.sync_service import SyncService
from app.schemas import SearchQuery, HydratedSearchResult, SyncPayload

router = APIRouter()

@router.get("/search", response_model=HydratedSearchResult)
def search(
    q: str = Query(..., min_length=1),
    type: str = Query(None, description="Entity type to filter by"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    service = SearchService(db)
    result = service.search_and_hydrate(query=q, entity_type=type, limit=limit, offset=offset)
    
    return {
        "metadata": {
            "query": q,
            "total_hits": result["total_hits"],
            "limit": limit,
            "offset": offset
        },
        "items": result["results"]
    }

# Fake endpoints to demonstrate synchronization logic
@router.post("/dummy-sync-create")
def create_dummy_entity(payload: SyncPayload, db: Session = Depends(get_db)):
    # Simulating your service layer creating a user or product...
    
    # After creation, call sync service:
    sync_service = SyncService(db)
    sync_service.on_create(
        entity_type=payload.entity_type, 
        entity_id=payload.entity_id, 
        title=payload.title, 
        description=payload.description, 
        extra_data=payload.metadata
    )
    return {"status": "synced"}
