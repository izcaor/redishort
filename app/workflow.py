import logging
from sqlalchemy.orm import Session
from app.database import models
from app.models.domain import ContentItem
import threading

logger = logging.getLogger(__name__)

def trigger_drafting(project_id: int, db: Session):
    project = db.query(models.VideoProject).filter(models.VideoProject.id == project_id).first()
    if not project or project.status != models.WorkflowState.NEW:
        return

    project.status = models.WorkflowState.DRAFTING
    db.commit()

    try:
        from text_processor import TextProcessor
        item = ContentItem(
            source_id=project.source_id,
            source_type=project.source_type,
            title=project.title,
            content_text=project.content_text,
            author=project.author,
            metadata=project.metadata_json or {}
        )

        processor = TextProcessor()
        result = processor.process_story(item)
        if not result:
            raise Exception("AI failed to generate script")

        project.script = result["script"]
        project.youtube_title = result["descriptions"].get("youtube_short_title", "")
        project.youtube_desc = result["descriptions"].get("youtube_short_desc", "")
        project.narrator_gender = result["narrator_gender"]
        project.status = models.WorkflowState.PENDING_APPROVAL

    except Exception as e:
        logger.error(f"Drafting failed for project {project_id}: {e}")
        project.error_message = str(e)
        project.status = models.WorkflowState.FAILED

    db.commit()

def trigger_generation_task(project_id: int):
    from app.database.database import SessionLocal
    db = SessionLocal()
    try:
        run_video_generation_pipeline(project_id, db)
    finally:
        db.close()

def run_video_generation_pipeline(project_id: int, db: Session):
    project = db.query(models.VideoProject).filter(models.VideoProject.id == project_id).first()
    if not project or project.status != models.WorkflowState.PENDING_APPROVAL:
        return

    project.status = models.WorkflowState.PROCESSING
    db.commit()

    try:
        from config import SESSIONS_FOLDER, WHISPER_MODEL
        import whisper
        from pathlib import Path
        import shutil
        from tts_generator import generate_audio
        from video_assembler import assemble_viral_video, get_random_video_segment

        session_folder = Path(SESSIONS_FOLDER) / f"project_{project.id}"
        session_folder.mkdir(parents=True, exist_ok=True)

        audio_path = session_folder / "audio.wav"
        success = generate_audio(project.script, str(audio_path), project.narrator_gender)
        if not success:
            raise Exception("Audio generation failed")

        bg_segment = get_random_video_segment(str(project.id))
        if not bg_segment:
             raise Exception("No background video segments available")

        output_video_path = session_folder / f"{project.id}_final.mp4"
        whisper_model = whisper.load_model(WHISPER_MODEL)

        assemble_viral_video(bg_segment, str(audio_path), str(output_video_path), whisper_model, project.narrator_gender)

        if output_video_path.exists() and output_video_path.stat().st_size > 1024:
             project.video_path = str(output_video_path)
             project.status = models.WorkflowState.COMPLETED
        else:
             raise Exception("Video assembly failed or output is empty")

    except Exception as e:
        logger.error(f"Video processing failed for project {project_id}: {e}")
        project.error_message = str(e)
        project.status = models.WorkflowState.FAILED

    db.commit()
