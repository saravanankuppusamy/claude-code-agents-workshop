def get_book(store, isbn):
    return store.load("books").get(isbn)

def list_by_author(store, author):
    return [b for b in store.load("books").values() if b["author"] == author]

def in_stock(store, isbn):
    book = get_book(store, isbn)
    return bool(book) and book.get("stock", 0) > 0
