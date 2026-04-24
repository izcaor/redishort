import pytest
from app.content_ingester import ContentIngester

def test_is_safe_url():
    ingester = ContentIngester()

    # Allowed public URLs
    assert ingester._is_safe_url("http://google.com") is True
    assert ingester._is_safe_url("https://example.com") is True

    # Blocked private/local IPs
    assert ingester._is_safe_url("http://127.0.0.1") is False
    assert ingester._is_safe_url("http://localhost") is False
    assert ingester._is_safe_url("http://192.168.1.1") is False
    assert ingester._is_safe_url("http://10.0.0.1") is False

    # Blocked non-HTTP schemes
    assert ingester._is_safe_url("file:///etc/passwd") is False
    assert ingester._is_safe_url("ftp://example.com") is False

def test_fetch_methods_reject_unsafe_urls(mocker):
    ingester = ContentIngester()

    # Reject private IP
    assert ingester.fetch_url("http://127.0.0.1") is None
    assert ingester.fetch_rss_feed("http://localhost") == []
    assert ingester._scrape_article_text("http://192.168.1.1") == ""

    # Reject non-http
    assert ingester.fetch_url("file:///etc/passwd") is None
    assert ingester.fetch_rss_feed("file:///etc/passwd") == []
    assert ingester._scrape_article_text("file:///etc/passwd") == ""

    # Reject unresolved or invalid
    assert ingester.fetch_url("http://invalid.domain.that.does.not.exist.com") is None
from unittest.mock import Mock, patch
from unittest.mock import MagicMock

def test_safe_fetch_redirect_loop(mocker):
    ingester = ContentIngester()

    # Mock _is_safe_url to always return True for testing redirect loop
    mocker.patch.object(ingester, '_is_safe_url', return_value=True)

    # Create a mock response that redirects to itself
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.status_code = 302
    mock_response.is_redirect = True
    mock_response.url = "http://example.com"
    mock_response.headers = {'Location': "http://example.com"}

    # Mock requests.get to return the mock response
    mocker.patch('requests.get', return_value=mock_response)

    assert ingester._safe_fetch("http://example.com") is None

def test_safe_fetch_redirect_to_unsafe(mocker):
    ingester = ContentIngester()

    # Create a mock response that redirects to an unsafe URL
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.status_code = 302
    mock_response.is_redirect = True
    mock_response.url = "http://example.com"
    mock_response.headers = {'Location': "http://127.0.0.1"}

    # Mock requests.get to return the mock response
    mocker.patch('requests.get', return_value=mock_response)

    # First URL is safe, second is unsafe
    def side_effect_is_safe_url(url):
        return url == "http://example.com"

    mocker.patch.object(ingester, '_is_safe_url', side_effect=side_effect_is_safe_url)

    assert ingester._safe_fetch("http://example.com") is None
