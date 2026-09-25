"""Book search (work stream: ISBN normalisation)."""
def normalise_isbn(raw):
    digits = "".join(ch for ch in raw if ch.isdigit() or ch in "Xx")
    return digits.upper()

def search(books, query):
    q = query.lower()
    return [b for b in books if q in b["title"].lower() or normalise_isbn(query) == b["isbn"]]
