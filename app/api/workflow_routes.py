from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import models
from pydantic import BaseModel
from app.workflow import trigger_drafting, run_video_generation_pipeline


router = APIRouter()

class UpdateScriptRequest(BaseModel):
    script: str
    youtube_title: str
    youtube_desc: str
    narrator_gender: str

@router.post("/projects/{project_id}/draft")
def start_drafting(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.VideoProject).filter(models.VideoProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status not in (models.WorkflowState.NEW, models.WorkflowState.FAILED):
        raise HTTPException(status_code=400, detail=f"Cannot draft project in state {project.status}")

    project.status = models.WorkflowState.DRAFTING
    db.commit()
    trigger_drafting.delay(project_id)
    return {"message": "Drafting started"}

@router.put("/projects/{project_id}/draft")
def update_draft(project_id: int, req: UpdateScriptRequest, db: Session = Depends(get_db)):
    project = db.query(models.VideoProject).filter(models.VideoProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != models.WorkflowState.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail="Can only update drafts pending approval")

    project.script = req.script
    project.youtube_title = req.youtube_title
    project.youtube_desc = req.youtube_desc
    project.narrator_gender = req.narrator_gender
    db.commit()
    return {"message": "Draft updated"}

@router.post("/projects/{project_id}/approve")
def approve_and_generate(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.VideoProject).filter(models.VideoProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != models.WorkflowState.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail="Project must be pending approval to generate video")

    run_video_generation_pipeline.delay(project_id)
    return {"message": "Video generation started"}
