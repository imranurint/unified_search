from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.repositories.search_repo import SearchRepository
from sqlalchemy import text
from app import models

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SearchRepository(db)

    def search_and_hydrate(self, query: str, entity_type: str = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        1. Fetch search results
        2. Group by entity_type
        3. Batch fetch hydrated models
        4. Reconstruct response
        """
        # 1. Fetch search hits
        hits = self.repo.search(query, entity_type, limit, offset)
        if not hits:
            return {"total_hits": 0, "results": []}

        # 2. Group by entity_type
        grouped_ids = {}
        for hit in hits:
            et = hit["entity_type"]
            eid = hit["entity_id"]
            if et not in grouped_ids:
                grouped_ids[et] = []
            grouped_ids[et].append(eid)

        # 3. Batch fetch hydrated data avoiding N+1
        hydrated_data = self._batch_hydrate(grouped_ids)

        # 4. Merge
        results = []
        for hit in hits:
            et = hit["entity_type"]
            eid = hit["entity_id"]
            
            # Use hydrated record if found, else just use the search data
            full_record = hydrated_data.get(et, {}).get(eid)
            
            results.append({
                "entity_type": et,
                "entity_id": eid,
                "rank": float(hit["rank"]),
                "headline": str(hit["headline"]) if hit["headline"] else "",
                "global_search_meta": hit["extra_data"],
                "data": full_record
            })

        return {
            "total_hits": len(hits), # Real count would be fetched separately or via count(*) over window
            "results": results
        }

    def _batch_hydrate(self, grouped_ids: Dict[str, List[int]]) -> Dict[str, Dict[int, Any]]:
        """
        Given a dict like {"user": [1, 2], "product": [5]}, fetch all at once.
        Returns: {"user": {1: {...}, 2: {...}}, "product": {5: {...}}}
        """
        result = {}
        
        # Mapping string name to ORM model
        type_to_model = {
            "user": models.User,
            "product": models.Product,
            "order": models.Order,
            "customer": models.Customer,
            "message": models.Message
        }

        for entity_type, ids in grouped_ids.items():
            if not ids or entity_type not in type_to_model:
                continue
                
            model = type_to_model[entity_type]
            records = self.db.query(model).filter(model.id.in_(ids)).all()
            
            result[entity_type] = {
                r.id: {c.name: getattr(r, c.name) for c in r.__table__.columns} 
                for r in records
            }
            
        return result
