from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
import json

class SearchRepository:
    def __init__(self, db: Session):
        self.db = db
        # Ensure FTS5 table exists for SQLite search
        self._init_fts()

    def _init_fts(self):
        self.db.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS global_search_fts USING fts5(
                entity_type, entity_id, title, description,
                content='global_search', content_rowid='id'
            );
        """))
        # Trigger to keep FTS in sync with main table
        self.db.execute(text("""
            CREATE TRIGGER IF NOT EXISTS global_search_ai AFTER INSERT ON global_search BEGIN
                INSERT INTO global_search_fts(rowid, entity_type, entity_id, title, description)
                VALUES (new.id, new.entity_type, new.entity_id, new.title, new.description);
            END;
        """))
        self.db.execute(text("""
            CREATE TRIGGER IF NOT EXISTS global_search_ad AFTER DELETE ON global_search BEGIN
                INSERT INTO global_search_fts(global_search_fts, rowid, entity_type, entity_id, title, description)
                VALUES('delete', old.id, old.entity_type, old.entity_id, old.title, old.description);
            END;
        """))
        self.db.execute(text("""
            CREATE TRIGGER IF NOT EXISTS global_search_au AFTER UPDATE ON global_search BEGIN
                INSERT INTO global_search_fts(global_search_fts, rowid, entity_type, entity_id, title, description)
                VALUES('delete', old.id, old.entity_type, old.entity_id, old.title, old.description);
                INSERT INTO global_search_fts(rowid, entity_type, entity_id, title, description)
                VALUES (new.id, new.entity_type, new.entity_id, new.title, new.description);
            END;
        """))
        self.db.commit()

    def upsert_search(self, entity_type: str, entity_id: int, title: str, description: Optional[str], extra_data: Optional[Dict[str, Any]] = None):
        """
        Upsert a record into global_search. FTS5 triggers handle the virtual table sync.
        """
        stmt = text("""
            INSERT INTO global_search (entity_type, entity_id, title, description, extra_data)
            VALUES (:entity_type, :entity_id, :title, :description, :extra_data)
            ON CONFLICT (entity_type, entity_id) DO UPDATE SET
                title = :title,
                description = :description,
                extra_data = :extra_data;
        """)
        meta_json = json.dumps(extra_data) if extra_data else "{}"
        self.db.execute(stmt, {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "title": title,
            "description": description,
            "extra_data": meta_json
        })
        self.db.commit()

    def delete_search_entry(self, entity_type: str, entity_id: int):
        stmt = text("DELETE FROM global_search WHERE entity_type = :entity_type AND entity_id = :entity_id")
        self.db.execute(stmt, {"entity_type": entity_type, "entity_id": entity_id})
        self.db.commit()

    def search(self, query: str, entity_type: Optional[str] = None, limit: int = 20, offset: int = 0):
        # Support prefix matching for partial word search by appending '*' to each term
        # e.g., 'str' -> 'str*'
        processed_query = ' '.join([f"{word}*" for word in query.split() if word])
        
        params = {"query": processed_query, "limit": limit, "offset": offset}
        # Use table alias 'gs' to avoid ambiguous column name error
        type_filter = "AND gs.entity_type = :entity_type" if entity_type else ""
        if entity_type:
            params["entity_type"] = entity_type

        sql = f"""
            SELECT 
                gs.id, gs.entity_type, gs.entity_id, gs.title, gs.description, gs.extra_data,
                bm25(global_search_fts) AS rank,
                snippet(global_search_fts, 3, '<b>', '</b>', '...', 10) as headline
            FROM global_search_fts fts
            JOIN global_search gs ON gs.id = fts.rowid
            WHERE global_search_fts MATCH :query
            {type_filter}
            ORDER BY rank
            LIMIT :limit OFFSET :offset
        """
        # Note: bm25 in SQLite is lower for better matches
        result = self.db.execute(text(sql), params).mappings().all()
        return result
