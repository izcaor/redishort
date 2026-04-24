import importlib
import sys
import types
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def scraper(monkeypatch):
    mock_requests = types.ModuleType('requests')
    mock_requests.Session = MagicMock

    mock_requests_adapters = types.ModuleType('requests.adapters')
    mock_requests_adapters.HTTPAdapter = MagicMock

    monkeypatch.setitem(sys.modules, 'requests', mock_requests)
    monkeypatch.setitem(sys.modules, 'requests.adapters', mock_requests_adapters)

    mock_urllib3 = types.ModuleType('urllib3')
    mock_urllib3_util = types.ModuleType('urllib3.util')
    mock_urllib3_retry = types.ModuleType('urllib3.util.retry')
    mock_urllib3_retry.Retry = MagicMock

    monkeypatch.setitem(sys.modules, 'urllib3', mock_urllib3)
    monkeypatch.setitem(sys.modules, 'urllib3.util', mock_urllib3_util)
    monkeypatch.setitem(sys.modules, 'urllib3.util.retry', mock_urllib3_retry)
    monkeypatch.setitem(sys.modules, 'app.models.domain', MagicMock())

    mock_config = MagicMock()
    mock_config.MIN_POST_TEXT_LENGTH = 80
    monkeypatch.setitem(sys.modules, 'config', mock_config)

    reddit_scraper = importlib.import_module('reddit_scraper')

    with patch.object(reddit_scraper.RedditScraper, '_load_processed_posts', return_value=set()):
        monkeypatch.setattr(reddit_scraper, 'MIN_POST_TEXT_LENGTH', 80)
        return reddit_scraper.RedditScraper()


def test_is_valid_post_valid(scraper):
    post = {
        'id': 'post1',
        'over_18': False,
        'is_video': False,
        'upvote_ratio': 0.9,
        'stickied': False,
        'is_self': True,
        'selftext': 'This is a long enough post body for testing purposes.' * 5
    }
    assert scraper._is_valid_post(post) is True


def test_is_valid_post_over_18(scraper):
    post = {
        'id': 'post1',
        'over_18': True,
        'is_video': False,
        'upvote_ratio': 0.9,
        'stickied': False,
        'is_self': True,
        'selftext': 'This is a long enough post body for testing purposes.' * 5
    }
    assert scraper._is_valid_post(post) is False


def test_is_valid_post_is_video(scraper):
    post = {
        'id': 'post1',
        'over_18': False,
        'is_video': True,
        'upvote_ratio': 0.9,
        'stickied': False,
        'is_self': True,
        'selftext': 'This is a long enough post body for testing purposes.' * 5
    }
    assert scraper._is_valid_post(post) is False


def test_is_valid_post_low_upvote_ratio(scraper):
    post = {
        'id': 'post1',
        'over_18': False,
        'is_video': False,
        'upvote_ratio': 0.7,
        'stickied': False,
        'is_self': True,
        'selftext': 'This is a long enough post body for testing purposes.' * 5
    }
    assert scraper._is_valid_post(post) is False


def test_is_valid_post_already_processed(scraper):
    scraper.processed_ids.add('post1')
    post = {
        'id': 'post1',
        'over_18': False,
        'is_video': False,
        'upvote_ratio': 0.9,
        'stickied': False,
        'is_self': True,
        'selftext': 'This is a long enough post body for testing purposes.' * 5
    }
    assert scraper._is_valid_post(post) is False


def test_is_valid_post_stickied(scraper):
    post = {
        'id': 'post1',
        'over_18': False,
        'is_video': False,
        'upvote_ratio': 0.9,
        'stickied': True,
        'is_self': True,
        'selftext': 'This is a long enough post body for testing purposes.' * 5
    }
    assert scraper._is_valid_post(post) is False


def test_is_valid_post_not_self(scraper):
    post = {
        'id': 'post1',
        'over_18': False,
        'is_video': False,
        'upvote_ratio': 0.9,
        'stickied': False,
        'is_self': False,
        'selftext': 'This is a long enough post body for testing purposes.' * 5
    }
    assert scraper._is_valid_post(post) is False


def test_is_valid_post_short_text(scraper):
    post = {
        'id': 'post1',
        'over_18': False,
        'is_video': False,
        'upvote_ratio': 0.9,
        'stickied': False,
        'is_self': True,
        'selftext': 'Too short'
    }
    assert scraper._is_valid_post(post) is False


def test_is_valid_post_removed(scraper):
    post = {
        'id': 'post1',
        'over_18': False,
        'is_video': False,
        'upvote_ratio': 0.9,
        'stickied': False,
        'is_self': True,
        'selftext': '[removed]'
    }
    assert scraper._is_valid_post(post) is False


def test_is_valid_post_deleted(scraper):
    post = {
        'id': 'post1',
        'over_18': False,
        'is_video': False,
        'upvote_ratio': 0.9,
        'stickied': False,
        'is_self': True,
        'selftext': '[deleted]'
    }
    assert scraper._is_valid_post(post) is False


def test_is_valid_post_missing_fields(scraper):
    # Testing missing upvote_ratio defaults to 0
    post = {
        'id': 'post1',
        'over_18': False,
        'is_video': False,
        # 'upvote_ratio' missing
        'stickied': False,
        'is_self': True,
        'selftext': 'This is a long enough post body for testing purposes.' * 5
    }
    assert scraper._is_valid_post(post) is False
