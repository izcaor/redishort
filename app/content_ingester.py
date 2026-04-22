import logging
import feedparser
import requests
from bs4 import BeautifulSoup
from app.models.domain import ContentItem

logger = logging.getLogger(__name__)

class ContentIngester:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def fetch_rss_feed(self, feed_url: str) -> list[ContentItem]:
        logger.info(f"Fetching RSS feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        items = []

        if feed.bozo:
            logger.error(f"Error parsing feed: {feed.bozo_exception}")
            return items

        for entry in feed.entries[:5]:
            try:
                content_text = self._scrape_article_text(entry.link)
                if not content_text and hasattr(entry, 'summary'):
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    content_text = soup.get_text(separator="\n", strip=True)

                if not content_text:
                     continue

                items.append(ContentItem(
                    source_id=entry.link,
                    source_type="rss",
                    title=entry.title,
                    content_text=content_text,
                    author=getattr(entry, 'author', None),
                    metadata={"url": entry.link, "published": getattr(entry, 'published', None)}
                ))
            except Exception as e:
                logger.error(f"Error processing RSS entry {entry.link}: {e}")
        return items

    def fetch_url(self, url: str) -> ContentItem | None:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            title = soup.title.string if soup.title else ""
            if not title:
                h1 = soup.find('h1')
                if h1: title = h1.get_text(strip=True)

            content_text = self._extract_main_content(soup)
            if not content_text:
                return None

            return ContentItem(
                source_id=url,
                source_type="url",
                title=title or "Extracted Article",
                content_text=content_text,
                metadata={"url": url}
            )
        except Exception as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return None

    def _scrape_article_text(self, url: str) -> str:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            return self._extract_main_content(soup)
        except Exception:
            return ""

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        article_candidates = soup.find_all(['article', 'main', 'div'], class_=lambda c: c and any(x in c.lower() for x in ['content', 'article', 'post', 'body']))

        best_text = ""
        best_len = 0
        if article_candidates:
            for candidate in article_candidates:
                paragraphs = candidate.find_all('p')
                text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
                if len(text) > best_len:
                    best_len = len(text)
                    best_text = text

        if not best_text:
            paragraphs = soup.find_all('p')
            best_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)
        return best_text
