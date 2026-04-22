from app.database.database import SessionLocal
from app.database import models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_db():
    db = SessionLocal()

    # Add a mock source
    source1 = models.ContentSource(source_type="rss", source_url="https://news.ycombinator.com/rss", name="Hacker News")
    db.add(source1)

    # Add some mock projects
    project1 = models.VideoProject(
        source_id="hn-123",
        source_type="rss",
        title="AI replaces programmers",
        content_text="A new AI model has been released that can write code...",
        status=models.WorkflowState.NEW
    )

    project2 = models.VideoProject(
        source_id="hn-124",
        source_type="rss",
        title="10 tips for faster code",
        content_text="Here are 10 tips to optimize your python code...",
        status=models.WorkflowState.PENDING_APPROVAL,
        script="[SCENE 1]\nNarrator: Want to write faster code?\n[SCENE 2]\nNarrator: Tip 1 is...",
        youtube_title="10 Python Tips",
        youtube_desc="Check out these 10 tips."
    )

    db.add(project1)
    db.add(project2)
    db.commit()
    db.close()
    logger.info("Database seeded.")

if __name__ == "__main__":
    seed_db()
