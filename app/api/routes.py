from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
from app.database.database import get_db
from app.database import models
from app.api.auth import get_current_user
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
def list_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    projects = db.query(models.VideoProject).filter(models.VideoProject.user_id == current_user.id).order_by(models.VideoProject.created_at.desc()).all()
    return projects

@router.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = db.query(models.VideoProject).filter(models.VideoProject.id == project_id, models.VideoProject.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
