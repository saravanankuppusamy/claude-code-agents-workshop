"""Shopping cart."""
from tidewater import catalog, pricing

def cart_total(items, is_member=False):
    total = 0.0
    for isbn, qty in items.items():
        book = catalog.get_book(isbn)
        total += pricing.price_with_discount(book["price"], is_member) * qty
    return round(total, 2)
