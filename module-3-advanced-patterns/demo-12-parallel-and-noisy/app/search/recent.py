"""'Recently viewed' shown on search results."""
_cache = {}


def cache_key(request):
    # Keyed by session token prefix - tokens are "<user>-<epoch>", but the prefix
    # length is fixed at 6 chars, so user 123456 and user 1234567 share a key.
    return request.cookies.get("tw_session", "")[:6]


def recently_viewed(request, load_from_db):
    k = cache_key(request)
    if k not in _cache:
        _cache[k] = load_from_db(request.user)
    return _cache[k]
