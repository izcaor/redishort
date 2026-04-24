"""
YouTube Uploader Module
-----------------------
Handles video uploads to YouTube using the Data API v3.
Supports scheduled publishing.
"""

import logging
from pathlib import Path
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import YOUTUBE_VIDEO_CATEGORY_ID

logger = logging.getLogger("RedishortApp.YouTubeUploader")
TOKEN_FILE = Path("token.json")


def get_authenticated_service():
    """
    Get authenticated YouTube API service.
    Returns None if credentials are invalid or missing.
    """
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            ["https://www.googleapis.com/auth/youtube.upload"]
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Ensure the file has secure permissions if it already exists
                if TOKEN_FILE.exists():
                    os.chmod(TOKEN_FILE, 0o600)
                # Securely open the file so only the owner can read/write
                fd = os.open(TOKEN_FILE, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
                with os.fdopen(fd, "w") as t:
                    t.write(creds.to_json())
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {e}")
                return None
        else:
            logger.error("No valid credentials. Run auth.py first.")
            return None

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube(video_path: Path, title: str, description: str,
                      tags: list, publish_at=None) -> str:
    """
    Upload a video to YouTube.

    Args:
        video_path: Path to video file
        title: Video title
        description: Video description
        tags: List of tags
        publish_at: Optional datetime for scheduled publishing (None = publish now)

    Returns:
        Video ID if successful, None otherwise
    """
    youtube = get_authenticated_service()
    if not youtube:
        return None

    # Build request body
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": YOUTUBE_VIDEO_CATEGORY_ID
        },
        "status": {
            "privacyStatus": "private" if publish_at else "public",
            "selfDeclaredMadeForKids": False
        }
    }

    # Add scheduled publish time if specified
    if publish_at:
        body["status"]["publishAt"] = publish_at.isoformat()
        logger.info(f"Scheduling video for: {publish_at.isoformat()}")

    try:
        media = MediaFileUpload(
            str(video_path),
            chunksize=-1,
            resumable=True
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        # Execute upload with progress tracking
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info(f"Upload progress: {progress}%")

        video_id = response.get("id")
        logger.info(f"✅ Upload complete. Video ID: {video_id}")
        return video_id

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return None
