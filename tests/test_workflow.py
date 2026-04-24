from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.workflow import trigger_drafting
from app.database import models
from app.database.database import Base

def test_trigger_drafting_error_handling():
    """
    Test that trigger_drafting correctly handles an exception during the drafting
    process, updates the project's error_message, sets the status to FAILED,
    and commits the changes to the database.
    """
    # Setup mock db session created by SessionLocal
    db = MagicMock()
    with patch("app.workflow.SessionLocal", return_value=db), patch("text_processor.TextProcessor") as MockTextProcessor:
        # Setup mock project
        project = MagicMock()
        project.id = 1
        project.status = models.WorkflowState.NEW
        project.source_id = "test"
        project.source_type = "test_type"
        project.title = "test_title"
        project.content_text = "test_content"
        project.author = "test_author"
        project.metadata_json = {}
        project.error_message = None
        db.query.return_value.filter.return_value.first.return_value = project

        mock_processor_instance = MockTextProcessor.return_value
        mock_processor_instance.process_story.side_effect = Exception("Test AI processing error")

        trigger_drafting(1)

        assert project.error_message == "Test AI processing error"
        assert project.status == models.WorkflowState.FAILED
        assert db.commit.call_count == 2
        db.close.assert_called_once()

def test_trigger_drafting_background_session_commits_pending_approval():
    """
    Regression test:
    ensure trigger_drafting updates a project already set to DRAFTING by the API
    and commits PENDING_APPROVAL using its own background SessionLocal session.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    # Simulate request-scoped session creating user/project and setting DRAFTING.
    request_db = TestingSessionLocal()
    user = models.User(email="user@example.com", hashed_password="hashed")
    request_db.add(user)
    request_db.commit()
    request_db.refresh(user)

    project = models.VideoProject(
        user_id=user.id,
        source_id="source-1",
        source_type="rss",
        title="Title",
        content_text="Body",
        author="Author",
        metadata_json={},
        status=models.WorkflowState.DRAFTING,
    )
    request_db.add(project)
    request_db.commit()
    project_id = project.id
    request_db.close()

    with patch("app.workflow.SessionLocal", TestingSessionLocal), patch("text_processor.TextProcessor") as MockTextProcessor:
        MockTextProcessor.return_value.process_story.return_value = {
            "script": "Generated script",
            "descriptions": {
                "youtube_short_title": "YT title",
                "youtube_short_desc": "YT desc",
            },
            "narrator_gender": "female",
        }

        trigger_drafting(project_id)

    verify_db = TestingSessionLocal()
    refreshed = verify_db.query(models.VideoProject).filter(models.VideoProject.id == project_id).first()
    assert refreshed.status == models.WorkflowState.PENDING_APPROVAL
    assert refreshed.script == "Generated script"
    assert refreshed.youtube_title == "YT title"
    assert refreshed.youtube_desc == "YT desc"
    assert refreshed.narrator_gender == "female"
    verify_db.close()
