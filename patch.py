import re

with open("reddit_scraper.py", "r") as f:
    content = f.read()

# Add lock and last_request_time to __init__
init_search = """    def __init__(self):
        self.session = requests.Session()
        self.processed_ids = self._load_processed_posts()"""
init_replace = """    def __init__(self):
        import threading
        self.session = requests.Session()
        self.processed_ids = self._load_processed_posts()
        self._lock = threading.Lock()
        self._last_req_time = 0.0"""

content = content.replace(init_search, init_replace)

fetch_search = """        try:
            response = self.session.get(url, headers=self._get_headers(), params=params, timeout=10)"""
fetch_replace = """        try:
            with self._lock:
                now = time.time()
                elapsed = now - self._last_req_time
                if elapsed < 0.3:
                    time.sleep(0.3 - elapsed)
                self._last_req_time = time.time()

            response = self.session.get(url, headers=self._get_headers(), params=params, timeout=10)"""

content = content.replace(fetch_search, fetch_replace)

fetch_comment_search = """        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)"""
fetch_comment_replace = """        try:
            with self._lock:
                now = time.time()
                elapsed = now - self._last_req_time
                if elapsed < 0.3:
                    time.sleep(0.3 - elapsed)
                self._last_req_time = time.time()

            response = self.session.get(url, headers=self._get_headers(), timeout=10)"""
content = content.replace(fetch_comment_search, fetch_comment_replace)

best_stories_search = """        for time_filter in ['day', 'week', 'month']:
            if len(candidates) >= num_stories * 3:  # Get extra candidates
                break

            for subreddit in hot_subreddits:
                posts = self._fetch_subreddit_posts(subreddit, sort="top", time_filter=time_filter, limit=25)
                time.sleep(0.3)  # Rate limiting

                for post in posts:
                    if self._is_valid_post(post):
                        score = (post.get("score", 0) * POST_SCORE_WEIGHT) + \\
                                (post.get("num_comments", 0) * COMMENT_SCORE_WEIGHT)
                        candidates.append((score, post))"""

best_stories_replace = """        import concurrent.futures

        for time_filter in ['day', 'week', 'month']:
            if len(candidates) >= num_stories * 3:  # Get extra candidates
                break

            def process_subreddit(subreddit):
                local_candidates = []
                posts = self._fetch_subreddit_posts(subreddit, sort="top", time_filter=time_filter, limit=25)
                for post in posts:
                    if self._is_valid_post(post):
                        score = (post.get("score", 0) * POST_SCORE_WEIGHT) + \\
                                (post.get("num_comments", 0) * COMMENT_SCORE_WEIGHT)
                        local_candidates.append((score, post))
                return local_candidates

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_subreddit = {executor.submit(process_subreddit, sub): sub for sub in hot_subreddits}
                for future in concurrent.futures.as_completed(future_to_subreddit):
                    try:
                        candidates.extend(future.result())
                    except Exception as e:
                        logger.debug(f"Error processing subreddit: {e}")"""

content = content.replace(best_stories_search, best_stories_replace)

with open("reddit_scraper.py", "w") as f:
    f.write(content)
