from fastapi import FastAPI
from app.api.endpoints import router as search_router
from app.api.entities import router as entity_router
from app.database import engine, Base

# Create tables if not exists (In production use Alembic or similar)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Unified Search API",
    description="Scalable global search using PostgreSQL Full-Text Search",
    version="1.0.0"
)

app.include_router(search_router, prefix="/api/v1")
app.include_router(entity_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Global Search API"}
