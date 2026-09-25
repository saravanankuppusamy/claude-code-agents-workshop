"""Request auth middleware."""
from app.auth.session import get_user


def require_login(request):
    user = get_user(request.cookies.get("tw_session"))
    if user is None:
        raise PermissionError("login required")      # checkout loses its state here
    request.user = user
    return request
