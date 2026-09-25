"""Book catalog."""
from tidewater import storage

def get_book(isbn):
    return storage.load("books").get(isbn)

def list_by_author(author):
    return [b for b in storage.load("books").values() if b["author"] == author]
