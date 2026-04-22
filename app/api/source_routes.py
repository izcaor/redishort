from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import models
from pydantic import BaseModel
from app.content_ingester import ContentIngester

router = APIRouter()
ingester = ContentIngester()

class URLIngestRequest(BaseModel):
    url: str

class RSSIngestRequest(BaseModel):
    url: str
    name: str

@router.post("/sources/url")
def ingest_url(req: URLIngestRequest, db: Session = Depends(get_db)):
    item = ingester.fetch_url(req.url)
    if not item:
        raise HTTPException(status_code=400, detail="Could not extract content from URL")

    project = models.VideoProject(
        source_id=item.source_id,
        source_type=item.source_type,
        title=item.title,
        content_text=item.content_text,
        author=item.author,
        metadata_json=item.metadata,
        status=models.WorkflowState.NEW
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"message": "URL ingested successfully", "project_id": project.id}

@router.post("/sources/rss")
def add_rss_source(req: RSSIngestRequest, db: Session = Depends(get_db)):
    source = models.ContentSource(source_type="rss", source_url=req.url, name=req.name)
    db.add(source)
    db.commit()
    db.refresh(source)
    return {"message": "RSS source added", "source_id": source.id}

@router.post("/sources/{source_id}/fetch")
def fetch_source_now(source_id: int, db: Session = Depends(get_db)):
    source = db.query(models.ContentSource).filter(models.ContentSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    if source.source_type == "rss":
        items = ingester.fetch_rss_feed(source.source_url)
        projects_created = 0
        for item in items:
            exists = db.query(models.VideoProject).filter(models.VideoProject.source_id == item.source_id).first()
            if not exists:
                project = models.VideoProject(
                    source_id=item.source_id,
                    source_type=item.source_type,
                    title=item.title,
                    content_text=item.content_text,
                    author=item.author,
                    metadata_json=item.metadata,
                    status=models.WorkflowState.NEW
                )
                db.add(project)
                projects_created += 1
        db.commit()
        return {"message": f"Fetched {len(items)} items, created {projects_created} new projects"}
    raise HTTPException(status_code=400, detail="Unsupported source type")

@router.get("/sources")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(models.ContentSource).all()
    return sources
