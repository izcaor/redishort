import time
import logging
from reddit_scraper import RedditScraper

logging.basicConfig(level=logging.INFO)

class MockScraper(RedditScraper):
    def _get_hot_subreddits(self):
        return [f"sub{i}" for i in range(10)]

    def _fetch_subreddit_posts(self, subreddit, sort, time_filter, limit):
        time.sleep(1.0) # simulate network latency
        return []

scraper = MockScraper()
start_time = time.time()
scraper.get_best_stories(num_stories=1)
end_time = time.time()
print(f"Time taken: {end_time - start_time:.2f} seconds")
