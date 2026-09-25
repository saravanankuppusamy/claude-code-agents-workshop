"""Search query handling."""
from app.search.recent import recently_viewed


def search(request, index, load_recent):
    results = index.lookup(request.args.get("q", ""))
    return {"results": results, "recent": recently_viewed(request, load_recent)}
