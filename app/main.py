from fastapi import FastAPI
from app.api.routes import router
from app.api.auth import router as auth_router
from app.api.source_routes import router as source_router
from app.api.workflow_routes import router as workflow_router
from app.database.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shorts Generator API", description="API for turning text content into shorts")

app.include_router(auth_router, prefix="/api")
app.include_router(router, prefix="/api")
app.include_router(source_router, prefix="/api")
app.include_router(workflow_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}
