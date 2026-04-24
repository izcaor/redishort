"""
Reddit Scraper Module (No API Required)
---------------------------------------
Scrapes public Reddit JSON endpoints to find viral stories.
No API key or approval needed.
"""

import random
import logging
import time
import requests
from app.models.domain import ContentItem
from pathlib import Path
from config import (
    ALL_SUBREDDITS, PROCESSED_POSTS_FILE, NUM_HOT_SUBREDDITS_TO_HUNT,
    MIN_POST_TEXT_LENGTH, MIN_COMMENT_TEXT_LENGTH,
    POST_SCORE_WEIGHT, COMMENT_SCORE_WEIGHT
)

logger = logging.getLogger(__name__)

# User agents to rotate (avoid rate limiting)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]


class RedditScraper:
    """
    Scrapes Reddit using public JSON endpoints.
    No API authentication required.
    """

    def __init__(self):
        import threading
        self.session = requests.Session()
        self.processed_ids = self._load_processed_posts()
        self._lock = threading.Lock()
        self._last_req_time = 0.0

    def _get_headers(self) -> dict:
        """Get randomized headers to avoid rate limiting."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _load_processed_posts(self) -> set:
        """Load set of already-processed post IDs to avoid duplicates."""
        log_path = Path(PROCESSED_POSTS_FILE)
        if not log_path.exists():
            return set()
        return set(log_path.read_text().splitlines())

    def _save_processed_post(self, post_id: str):
        """Append a post ID to the processed posts log."""
        with open(PROCESSED_POSTS_FILE, "a") as f:
            f.write(f"{post_id}\n")
        self.processed_ids.add(post_id)

    def _fetch_subreddit_posts(self, subreddit: str, sort: str = "top", time_filter: str = "day", limit: int = 25) -> list:
        """
        Fetch posts from a subreddit using public JSON endpoint.

        Args:
            subreddit: Name of subreddit (without r/)
            sort: 'hot', 'top', 'new'
            time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'
            limit: Max posts to fetch (max 100)
        """
        url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
        params = {"limit": limit, "t": time_filter}

        try:
            with self._lock:
                now = time.time()
                elapsed = now - self._last_req_time
                if elapsed < 0.3:
                    time.sleep(0.3 - elapsed)
                self._last_req_time = time.time()

            response = self.session.get(url, headers=self._get_headers(), params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            posts = data.get("data", {}).get("children", [])
            return [post["data"] for post in posts if post.get("data")]

        except Exception as e:
            logger.debug(f"Failed to fetch r/{subreddit}: {e}")
            return []

    def _get_subreddit_temperature(self, subreddit: str) -> int:
        """Calculate subreddit activity score based on recent posts."""
        posts = self._fetch_subreddit_posts(subreddit, sort="hot", limit=10)
        return sum(post.get("score", 0) for post in posts if not post.get("stickied"))

    def _get_hot_subreddits(self) -> list[str]:
        """Get the most active subreddits from the configured list."""
        logger.info("--- Measuring subreddit temperature ---")
        temps = {}

        for name in ALL_SUBREDDITS:
            temps[name] = self._get_subreddit_temperature(name)
            time.sleep(0.5)  # Rate limiting

        hot_subs = sorted(temps, key=temps.get, reverse=True)[:NUM_HOT_SUBREDDITS_TO_HUNT]
        logger.info(f"Hunting in top {len(hot_subs)} subreddits: {', '.join(hot_subs[:5])}...")
        return hot_subs

    def _fetch_top_comment(self, subreddit: str, post_id: str) -> str:
        """Fetch the top comment from a post."""
        url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"

        try:
            with self._lock:
                now = time.time()
                elapsed = now - self._last_req_time
                if elapsed < 0.3:
                    time.sleep(0.3 - elapsed)
                self._last_req_time = time.time()

            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()

            data = response.json()
            if len(data) < 2:
                return ""

            comments = data[1].get("data", {}).get("children", [])
            for comment in comments:
                comment_data = comment.get("data", {})
                body = comment_data.get("body", "")
                author = comment_data.get("author", "")

                if (body and
                    len(body) > MIN_COMMENT_TEXT_LENGTH and
                    "bot" not in author.lower() and
                    not comment_data.get("stickied")):
                    return f"The people responded: {body}"

            return ""

        except Exception:
            return ""

    def _is_valid_post(self, post: dict) -> bool:
        """Check if a post meets the criteria for processing."""
        post_id = post.get("id", "")
        selftext = post.get("selftext", "")

        return (
            post_id not in self.processed_ids and
            not post.get("stickied") and
            post.get("is_self", False) and
            len(selftext) >= MIN_POST_TEXT_LENGTH and
            selftext != "[removed]" and
            selftext != "[deleted]"
        )

    def _create_story_package(self, post: dict, score: float) -> dict:
        """Package a post into a story dict for processing."""
        post_id = post.get("id", "")
        title = post.get("title", "")
        subreddit = post.get("subreddit", "")
        selftext = post.get("selftext", "")

        logger.info(f"-> Selected: '{title[:60]}...' from r/{subreddit} (Score: {int(score)})")

        # Fetch top comment
        top_comment = self._fetch_top_comment(subreddit, post_id)
        time.sleep(0.5)  # Rate limiting

        full_story_text = f"Title: {title}\n\nBody: {selftext}\n\nTop Comment: {top_comment}"
        self._save_processed_post(post_id)

        return {
            "id": post_id,
            "title": title,
            "story_text": full_story_text,
            "subreddit": subreddit
        }

    def get_best_stories(self, num_stories: int = 1) -> list[ContentItem]:
        """
        Main entry point. Find and return the best stories.
        Uses temperature-based subreddit selection and multi-timeframe scanning.
        """
        logger.info("\n[HUNTER MODULE]: Starting story search (scraping mode)...")
        hot_subreddits = self._get_hot_subreddits()
        candidates = []

        import concurrent.futures

        for time_filter in ['day', 'week', 'month']:
            if len(candidates) >= num_stories * 3:  # Get extra candidates
                break

            def process_subreddit(subreddit):
                local_candidates = []
                posts = self._fetch_subreddit_posts(subreddit, sort="top", time_filter=time_filter, limit=25)
                for post in posts:
                    if self._is_valid_post(post):
                        score = (post.get("score", 0) * POST_SCORE_WEIGHT) + \
                                (post.get("num_comments", 0) * COMMENT_SCORE_WEIGHT)
                        local_candidates.append((score, post))
                return local_candidates

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_subreddit = {executor.submit(process_subreddit, sub): sub for sub in hot_subreddits}
                for future in concurrent.futures.as_completed(future_to_subreddit):
                    try:
                        candidates.extend(future.result())
                    except Exception as e:
                        logger.debug(f"Error processing subreddit: {e}")

        # Sort by score and return top stories
        candidates.sort(key=lambda x: x[0], reverse=True)

        stories = []
        for score, post in candidates[:num_stories]:
            stories.append(self._create_story_package(post, score))

        logger.info(f"Found {len(stories)} stories ready for processing.")
        return stories
