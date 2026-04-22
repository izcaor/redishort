from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import models
from app.api.auth import get_current_user
from pydantic import BaseModel
from app.workflow import trigger_drafting, trigger_generation_task
import threading

router = APIRouter()

class UpdateScriptRequest(BaseModel):
    script: str
    youtube_title: str
    youtube_desc: str
    narrator_gender: str

@router.post("/projects/{project_id}/draft")
def start_drafting(project_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(models.VideoProject).filter(models.VideoProject.id == project_id, models.VideoProject.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status not in (models.WorkflowState.NEW, models.WorkflowState.FAILED):
        raise HTTPException(status_code=400, detail=f"Cannot draft project in state {project.status}")

    project.status = models.WorkflowState.DRAFTING
    db.commit()
    background_tasks.add_task(trigger_drafting, project_id, db)
    return {"message": "Drafting started"}

@router.put("/projects/{project_id}/draft")
def update_draft(project_id: int, req: UpdateScriptRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = db.query(models.VideoProject).filter(models.VideoProject.id == project_id, models.VideoProject.user_id == current_user.id).first()
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
def approve_and_generate(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = db.query(models.VideoProject).filter(models.VideoProject.id == project_id, models.VideoProject.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != models.WorkflowState.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail="Project must be pending approval to generate video")

    thread = threading.Thread(target=trigger_generation_task, args=(project_id,))
    thread.start()
    return {"message": "Video generation started"}
