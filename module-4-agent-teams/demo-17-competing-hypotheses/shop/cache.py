"""Availability cache in front of the store (TTL in seconds)."""
import time

from shop import store

TTL_SECONDS = 5.0
_cache = {}


def available(isbn, use_cache=True):
    if not use_cache:
        return store.read_stock(isbn)
    hit = _cache.get(isbn)
    if hit and time.time() - hit[1] < TTL_SECONDS:
        return hit[0]
    value = store.read_stock(isbn)
    _cache[isbn] = (value, time.time())
    return value


def invalidate(isbn):
    _cache.pop(isbn, None)
