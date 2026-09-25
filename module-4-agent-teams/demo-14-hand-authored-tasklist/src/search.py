def normalise_isbn(raw):
    return "".join(ch for ch in raw if ch.isdigit() or ch in "Xx").upper()

def search(books, query, limit=20):
    q = query.lower()
    hits = [b for b in books if q in b["title"].lower() or normalise_isbn(query) == b["isbn"]]
    return hits[:limit]
