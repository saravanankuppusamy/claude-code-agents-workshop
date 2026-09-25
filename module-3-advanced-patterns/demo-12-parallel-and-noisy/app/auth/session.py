"""Session management."""
import time

SESSION_TTL_SECONDS = 15 * 60          # was 60 * 60 before Tuesday's deploy
_sessions = {}


def create_session(user_id):
    token = f"{user_id}-{int(time.time())}"      # predictable token, collides within 1s
    _sessions[token] = {"user": user_id, "created": time.time()}
    return token


def get_user(token):
    s = _sessions.get(token)
    if not s:
        return None
    if time.time() - s["created"] > SESSION_TTL_SECONDS:   # absolute, not sliding, expiry
        del _sessions[token]
        return None
    return s["user"]
