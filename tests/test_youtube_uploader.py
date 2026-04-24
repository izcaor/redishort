import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime, timezone
from youtube_uploader import upload_to_youtube, get_authenticated_service

@pytest.fixture
def mock_service():
    with patch("youtube_uploader.get_authenticated_service") as mock:
        yield mock

@pytest.fixture
def mock_media():
    with patch("youtube_uploader.MediaFileUpload") as mock:
        yield mock

def test_upload_success(mock_service, mock_media):
    mock_youtube = MagicMock()
    mock_service.return_value = mock_youtube

    mock_request = MagicMock()
    mock_youtube.videos().insert.return_value = mock_request

    # Mock next_chunk to simulate completing upload
    mock_status = MagicMock()
    mock_status.progress.return_value = 1.0
    mock_request.next_chunk.return_value = (mock_status, {"id": "test_video_id"})

    video_path = Path("test.mp4")
    result = upload_to_youtube(video_path, "Test Title", "Test Desc", ["test"])

    assert result == "test_video_id"
    mock_youtube.videos().insert.assert_called_once()
    kwargs = mock_youtube.videos().insert.call_args[1]
    assert kwargs["body"]["snippet"]["title"] == "Test Title"
    assert kwargs["body"]["status"]["privacyStatus"] == "public"

def test_upload_scheduled(mock_service, mock_media):
    mock_youtube = MagicMock()
    mock_service.return_value = mock_youtube

    mock_request = MagicMock()
    mock_youtube.videos().insert.return_value = mock_request

    mock_request.next_chunk.return_value = (None, {"id": "test_scheduled_id"})

    publish_time = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc)
    result = upload_to_youtube(Path("test.mp4"), "Title", "Desc", [], publish_at=publish_time)

    assert result == "test_scheduled_id"
    kwargs = mock_youtube.videos().insert.call_args[1]
    assert kwargs["body"]["status"]["privacyStatus"] == "private"
    assert kwargs["body"]["status"]["publishAt"] == publish_time.isoformat()

def test_upload_no_auth(mock_service):
    mock_service.return_value = None

    result = upload_to_youtube(Path("test.mp4"), "Title", "Desc", [])

    assert result is None

def test_upload_exception(mock_service, mock_media):
    mock_youtube = MagicMock()
    mock_service.return_value = mock_youtube

    mock_youtube.videos().insert.side_effect = Exception("API Error")

    result = upload_to_youtube(Path("test.mp4"), "Title", "Desc", [])

    assert result is None
