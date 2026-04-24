import time
import logging
from reddit_scraper import RedditScraper

logging.basicConfig(level=logging.INFO)

scraper = RedditScraper()
# mock _get_hot_subreddits to avoid the slow initial step and focus on the inner loops
scraper._get_hot_subreddits = lambda: ['AskReddit', 'Showerthoughts', 'tifu', 'personalfinance', 'relationship_advice']

start_time = time.time()
stories = scraper.get_best_stories(num_stories=1)
end_time = time.time()

print(f"Time taken: {end_time - start_time:.2f} seconds")
print(f"Found {len(stories)} stories")
