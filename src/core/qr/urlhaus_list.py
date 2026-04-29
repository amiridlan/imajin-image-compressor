"""
URLhaus blocklist manager.

Downloads and caches the URLhaus plain-text threat feed from abuse.ch.
The feed contains known-malicious URLs updated continuously by the community.

Cache location: <user home>/.imajin/urlhaus.txt
Refresh interval: 24 hours
"""

import os
import time
import threading

URLHAUS_URL = 'https://urlhaus.abuse.ch/downloads/text/'
CACHE_DIR = os.path.join(os.path.expanduser('~'), '.imajin')
CACHE_FILE = os.path.join(CACHE_DIR, 'urlhaus.txt')
MAX_AGE_SECONDS = 86400   # 24 hours

_lock = threading.Lock()
_cached_set: set | None = None


def get_blocklist() -> set:
    """
    Return the URLhaus blocklist as a set of lowercase URL strings.
    Loads from cache file; refreshes in background if stale.
    """
    global _cached_set
    with _lock:
        if _cached_set is not None:
            return _cached_set

    urls = _load_from_disk()
    with _lock:
        _cached_set = urls

    if _is_stale():
        threading.Thread(target=_refresh_cache, daemon=True).start()

    return _cached_set


def force_refresh() -> bool:
    """Synchronously download and update the cache. Returns True on success."""
    return _refresh_cache()


def _load_from_disk() -> set:
    if not os.path.exists(CACHE_FILE):
        _refresh_cache()
    if not os.path.exists(CACHE_FILE):
        return set()
    return _parse_file(CACHE_FILE)


def _parse_file(path: str) -> set:
    urls = set()
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.add(line.lower())
    except Exception:
        pass
    return urls


def _is_stale() -> bool:
    if not os.path.exists(CACHE_FILE):
        return True
    age = time.time() - os.path.getmtime(CACHE_FILE)
    return age > MAX_AGE_SECONDS


def _refresh_cache() -> bool:
    global _cached_set
    try:
        import requests
        resp = requests.get(URLHAUS_URL, timeout=15)
        resp.raise_for_status()

        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            f.write(resp.text)

        new_set = _parse_file(CACHE_FILE)
        with _lock:
            _cached_set = new_set
        return True
    except Exception:
        return False


def cache_exists() -> bool:
    return os.path.exists(CACHE_FILE)


def cache_size() -> int:
    """Number of URLs currently in the in-memory blocklist."""
    with _lock:
        return len(_cached_set) if _cached_set is not None else 0
