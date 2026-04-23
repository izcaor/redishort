from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.routes import router as projects_router
from app.api.source_routes import router as source_router
from app.api.workflow_routes import router as workflow_router
from app.database.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shorts Generator API", description="API for turning text content into shorts")

app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(source_router, prefix="/api", tags=["sources"])
app.include_router(workflow_router, prefix="/api", tags=["workflows"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
