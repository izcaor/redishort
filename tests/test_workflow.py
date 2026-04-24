import pytest
from unittest.mock import MagicMock, patch
from app.workflow import trigger_drafting
from app.database import models
import text_processor

def test_trigger_drafting_error_handling():
    """
    Test that trigger_drafting correctly handles an exception during the drafting
    process, updates the project's error_message, sets the status to FAILED,
    and commits the changes to the database.
    """
    # Setup mock db session
    db = MagicMock()

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

    # Configure db query to return the mock project
    db.query.return_value.filter.return_value.first.return_value = project

    # Mock TextProcessor to raise an exception
    with patch("text_processor.TextProcessor") as MockTextProcessor:
        mock_processor_instance = MockTextProcessor.return_value
        # Use side_effect to raise an Exception when process_story is called
        mock_processor_instance.process_story.side_effect = Exception("Test AI processing error")

        # Call the function
        trigger_drafting(1, db)

        # Verify the error handling logic
        assert project.error_message == "Test AI processing error"
        assert project.status == models.WorkflowState.FAILED

        # Verify db.commit() was called twice:
        # 1. To set status to DRAFTING
        # 2. In the finally/end block to save the FAILED status and error message
        assert db.commit.call_count == 2
