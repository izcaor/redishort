import logging
import feedparser
import requests
import socket
import ipaddress
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from app.models.domain import ContentItem

logger = logging.getLogger(__name__)

class ContentIngester:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def _is_safe_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Get all resolved IPs
            addr_infos = socket.getaddrinfo(hostname, None)
            for addr_info in addr_infos:
                ip = addr_info[4][0]
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                    return False

            return True
        except Exception as e:
            logger.error(f"Error validating URL {url}: {e}")
            return False

    def _safe_fetch(self, url: str):
        current_url = url
        for _ in range(5): # Max redirects
            if not self._is_safe_url(current_url):
                logger.error(f"Unsafe URL rejected: {current_url}")
                return None
            try:
                response = requests.get(current_url, headers=self.headers, timeout=10, allow_redirects=False)
                if response.is_redirect:
                    location = response.headers.get('Location')
                    if not location:
                        return None
                    from urllib.parse import urljoin
                    current_url = urljoin(response.url, location)
                    continue
                response.raise_for_status()
                return response
            except Exception as e:
                logger.error(f"Failed to fetch {current_url}: {e}")
                return None
        logger.error(f"Too many redirects for {url}")
        return None

    def fetch_rss_feed(self, feed_url: str) -> list[ContentItem]:
        logger.info(f"Fetching RSS feed: {feed_url}")
        response = self._safe_fetch(feed_url)
        if not response:
            return []

        feed = feedparser.parse(response.content)
        items = []

        if feed.bozo:
            logger.error(f"Error parsing feed: {feed.bozo_exception}")
            return items

        for entry in feed.entries[:5]:
            try:
                link = entry.get('link')
                if not link:
                    continue
                content_text = self._scrape_article_text(link)
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
        response = self._safe_fetch(url)
        if not response:
            return None

        try:
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
            logger.error(f"Failed to process fetched URL content for {url}: {e}")
            return None

    def _scrape_article_text(self, url: str) -> str:
        response = self._safe_fetch(url)
        if not response:
            return ""
        try:
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
