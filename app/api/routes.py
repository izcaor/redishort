from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
from app.database.database import get_db
from app.database import models
from pydantic import BaseModel

router = APIRouter()

class VideoProjectResponse(BaseModel):
    id: int
    title: str
    status: str
    script: str | None = None
    created_at: Any

    model_config = {
        'from_attributes': True
    }

@router.get("/projects", response_model=List[VideoProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(models.VideoProject).order_by(models.VideoProject.created_at.desc()).all()
    return projects

@router.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.VideoProject).filter(models.VideoProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
