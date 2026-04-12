# Unified Global Search with FastAPI & PostgreSQL

This repository contains a production-ready global search system using PostgreSQL Full-Text Search.

## Architecture Decisions

1. **Table Design**: `global_search` acts as an index table mapping to domain tables (`User`, `Product`, etc.). By combining a tsvector index and metadata, we can perform hyper-fast entity filtering and ranking.
2. **Sync Service Layer**: Avoids complex DB triggers. Relying on application-layer logic allows sending updates to message queues, decoupling microservices easily if the application expands.
3. **Hydration**: The API searches `global_search`. It batches IDs and makes a single `IN` query per entity type rather than iterating one by one (solving the N+1 problem). This is highly scalable.
4. **Ranking & Indexing**: Uses GIN indexes. `tsvector(title) || tsvector(description)` with `setweight` provides customizable scoring algorithms. Trigram (`pg_trgm`) can be easily toggled for fuzzy matching.
5. **Pagination**: Built-in limit/offset capabilities.

## Code Structure

- `app/api/`: Routing (`endpoints.py`) and DI (`dependencies.py`).
- `app/services/`: Application core.
  - `search_service.py`: FTS evaluation and DB Hydration Logic.
  - `sync_service.py`: The single entry to synchronize updates to FTS table.
- `app/repositories/`: Single place for raw logic (like `ON CONFLICT DO UPDATE`).
- `app/models.py`: SQLAlchemy schemas mapping to PostgreSQL.
- `scripts/backfill.py`: A safe initialization script spanning millions of records seamlessly using raw SQL and `INSERT ... SELECT`.

## SQL Scripts (For Production)

If running raw schema instead of SQLAlchemy, the critical components are:

```sql
-- 1. Create table
CREATE TABLE global_search (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    metadata JSONB,
    search_vector TSVECTOR
);

-- 2. Constraints and Indexes
ALTER TABLE global_search ADD CONSTRAINT uq_entity_type_id UNIQUE (entity_type, entity_id);

CREATE INDEX idx_global_search_entity ON global_search (entity_type);
CREATE INDEX idx_global_search_vector ON global_search USING GIN (search_vector);
```

## Advanced Enhancements

- **Fuzzy Fallback**: If `ts_rank` yields 0 rows, use `pg_trgm`: `WHERE title % :query`.
- **Async Queueing**: Turn `SyncService.on_create` into a Celery task.
- **Partial Hydration**: Pre-store minimal fields inside JSON metadata so hydration isn't even needed for basic listing.
