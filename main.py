"""
Main Application Orchestrator
-----------------------------
Entry point and brain of the application. Runs the continuous loop to produce
and publish videos according to schedule.

Responsibilities:
1. Configure logging and directory structure.
2. Load AI models (TTS and Whisper) into memory.
3. Run an infinite loop that:
   a. Calculates the next publish window.
   b. Performs maintenance tasks (background video supply).
   c. Orchestrates the full pipeline: find story -> process text ->
      generate audio -> assemble video -> upload to YouTube.
   d. Manages publish scheduling logic.
   e. Controls wait time until next work cycle.
4. Handles memory cleanup and old session management.
"""

import gc
import torch
import logging
import time
import whisper
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from dotenv import load_dotenv
import shutil
import os
import re

load_dotenv()

from config import *
from reddit_scraper import RedditScraper
from text_processor import TextProcessor
from tts_generator import generate_audio, preload_coqui_models
from video_downloader import download_new_source_videos
from video_segmenter import process_new_videos_into_segments
from video_assembler import assemble_viral_video, get_random_video_segment, segment_manager
from youtube_uploader import upload_to_youtube

def setup_logging(session_path: Path) -> logging.Logger:
    """Configure logging system to save log per session and show in console."""
    log_file = session_path / "session_log.txt"
    logger = logging.getLogger("RedishortApp")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s"))
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger

def clean_old_sessions():
    """Delete old session folders to prevent disk from filling up."""
    logger = logging.getLogger("RedishortApp")
    sessions_path = Path(SESSIONS_FOLDER)
    if not sessions_path.exists(): return

    session_pattern = re.compile(r"^\d{8}_\d{6}$")
    valid_sessions = sorted(
        [d for d in sessions_path.iterdir() if d.is_dir() and session_pattern.match(d.name)],
        reverse=True
    )

    to_delete = valid_sessions[MAX_SESSIONS_TO_KEEP:]
    if to_delete:
        logger.info(f"Cleaning {len(to_delete)} old sessions...")
        for session_dir in to_delete:
            try:
                shutil.rmtree(session_dir)
            except OSError as e:
                logger.error(f"Error deleting old session {session_dir.name}: {e}")

def ensure_directories():
    """Ensure all required application directories exist."""
    Path(ASSETS_FOLDER).mkdir(exist_ok=True)
    Path(SESSIONS_FOLDER).mkdir(exist_ok=True)
    Path(RAW_VIDEOS_FOLDER).mkdir(exist_ok=True)
    Path(SEGMENTS_FOLDER).mkdir(exist_ok=True)

def has_video_files(directory: Path, extensions=('.mp4', '.mov', '.mkv')) -> int:
    """Count how many video files are in a directory."""
    if not directory.is_dir(): return 0
    return len([f for f in directory.iterdir() if f.suffix.lower() in extensions])

def maintenance_and_setup(logger: logging.Logger):
    """
    Run maintenance tasks to ensure sufficient assets are available.
    Downloads raw videos if needed, processes them into segments.
    """
    logger.info("--- Maintenance and Supply Cycle Started ---")
    raw_videos_dir = Path(RAW_VIDEOS_FOLDER)

    videos_to_download = MAX_RAW_VIDEOS_IN_LIBRARY - has_video_files(raw_videos_dir)
    if videos_to_download > 0:
        logger.info(f"Raw video library needs {videos_to_download} new video(s). Starting download...")
        download_new_source_videos(num_to_download=videos_to_download)

    if has_video_files(raw_videos_dir) > 0:
        logger.info("Processing existing raw videos into segments...")
        process_new_videos_into_segments()

def get_segment_count() -> int:
    """Count the number of video segments ready to use."""
    segments_dir = Path(SEGMENTS_FOLDER)
    if not segments_dir.is_dir(): return 0
    return len([f for f in segments_dir.iterdir() if f.is_file() and f.suffix == '.mp4'])

def get_next_publish_time(schedule: list, timezone_str: str) -> datetime:
    """
    Calculate next publish datetime based on schedule
    and current time in the specified timezone.
    """
    tz = pytz.timezone(timezone_str)
    now_in_tz = datetime.now(tz)

    for time_str in sorted(schedule):
        hour, minute = map(int, time_str.split(':'))
        next_publish_dt = now_in_tz.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_publish_dt > now_in_tz:
            return next_publish_dt

    tomorrow_in_tz = now_in_tz + timedelta(days=1)
    first_hour, first_minute = map(int, sorted(schedule)[0].split(':'))
    return tomorrow_in_tz.replace(hour=first_hour, minute=first_minute, second=0, microsecond=0)

def main_loop():
    """The main loop and orchestrator for the entire application."""
    session_folder = Path(SESSIONS_FOLDER) / datetime.now().strftime("%Y%m%d_%H%M%S")
    session_folder.mkdir(parents=True, exist_ok=True)
    logger = setup_logging(session_folder)

    logger.info("=" * 60)
    logger.info("===   AUTONOMOUS YOUTUBE PUBLISHING SYSTEM STARTED   ===")
    logger.info(f"===   Schedule ({TIMEZONE}): {', '.join(PUBLISHING_SCHEDULE)}   ===")
    logger.info(f"===   Publish Tolerance: {PUBLISH_TOLERANCE_MINUTES} minutes   ===")
    logger.info("=" * 60)

    preload_coqui_models()
    text_processor = TextProcessor()
    reddit_scraper = RedditScraper()
    whisper_model = whisper.load_model(WHISPER_MODEL)

    while True:
        try:
            # --- PLANNING AND MAINTENANCE PHASE ---
            target_publish_time = get_next_publish_time(PUBLISHING_SCHEDULE, TIMEZONE)
            logger.info(f"\n--- Next publish target: {target_publish_time.strftime('%Y-%m-%d %H:%M:%S %Z')} ---")

            if get_segment_count() < MIN_SEGMENTS_IN_LIBRARY:
                logger.warning(f"Low segment inventory ({get_segment_count()}/{MIN_SEGMENTS_IN_LIBRARY}). Running maintenance...")
                maintenance_and_setup(logger)

            # --- CONTENT PRODUCTION PHASE ---
            logger.info("-> Searching for the best available story...")
            stories = reddit_scraper.get_best_stories(num_stories=1)
            if not stories:
                logger.warning("No valid stories found. Retrying in 15 minutes.")
                time.sleep(900); continue

            story = stories[0]
            story_id, story_title = story.source_id, story.title
            story_folder = session_folder / f"story_{story_id}"
            story_folder.mkdir(exist_ok=True)

            logger.info(f">>> Producing video for story: '{story_title[:60]}...'")
            content_pack = text_processor.process_story(story)
            if not content_pack or not content_pack.get("descriptions"):
                logger.error(f"Failed to process text for {story_id}. Searching new story."); continue

            audio_path = story_folder / "audio.wav"
            if not generate_audio(content_pack["script"], str(audio_path), content_pack["narrator_gender"]):
                 logger.error(f"Failed to generate audio for {story_id}. Searching new story."); continue

            background_segment = get_random_video_segment(story_id)
            output_video_path = story_folder / f"{story_id}_final.mp4"

            assemble_viral_video(background_segment, str(audio_path), str(output_video_path), whisper_model, content_pack["narrator_gender"])

            # --- PUBLISHING AND CLEANUP PHASE ---
            if output_video_path.exists() and output_video_path.stat().st_size > 1024:

                publish_time_for_api = target_publish_time
                current_time_in_tz = datetime.now(pytz.timezone(TIMEZONE))
                if current_time_in_tz >= target_publish_time:
                    time_passed = current_time_in_tz - target_publish_time
                    if time_passed.total_seconds() / 60 <= PUBLISH_TOLERANCE_MINUTES:
                        logger.warning("Production took time, but within tolerance. Publishing now.")
                        publish_time_for_api = None
                    else:
                        logger.warning(f"Production exceeded tolerance. Missed slot at {target_publish_time.strftime('%H:%M')}.")
                        new_target_time = get_next_publish_time(PUBLISHING_SCHEDULE, TIMEZONE)
                        logger.info(f"Re-scheduling for next slot: {new_target_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                        publish_time_for_api = new_target_time

                yt_title = content_pack["descriptions"]["youtube_short_title"]
                yt_desc = content_pack["descriptions"]["youtube_short_desc"]
                yt_tags = ["reddit", "stories", "askreddit", "storytime", story.metadata.get("subreddit", "story")]

                video_id = upload_to_youtube(
                    video_path=output_video_path, title=yt_title, description=yt_desc,
                    tags=yt_tags, publish_at=publish_time_for_api
                )

                if video_id:
                    logger.info(f"✅ Video for {story_id} uploaded successfully.")
                    segment_manager.consume_segment(story_id)
                    shutil.rmtree(story_folder)
                else:
                    logger.critical(f"Video for {story_id} created but upload failed. Will retry next cycle.")

            # --- WAIT PHASE ---
            logger.info("-> Starting post-production memory cleanup...")
            del story, stories, content_pack, background_segment
            gc.collect()

            now_in_tz = datetime.now(pytz.timezone(TIMEZONE))
            next_slot_after_job = get_next_publish_time(PUBLISHING_SCHEDULE, TIMEZONE)
            time_to_next_slot = next_slot_after_job - now_in_tz

            sleep_duration = max(60, time_to_next_slot.total_seconds() - 3600)
            logger.info(f"Production paused. Next work cycle starts in {sleep_duration/3600:.2f} hours.")
            time.sleep(sleep_duration)

        except Exception as e:
            logger.critical(f"Unexpected error in main loop: {e}", exc_info=True)
            logger.info("Waiting 10 minutes before retrying cycle...")
            time.sleep(600)

if __name__ == "__main__":
    ensure_directories()
    clean_old_sessions()
    main_loop()
