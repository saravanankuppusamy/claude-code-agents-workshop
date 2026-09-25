"""Checkout: approve an order if stock is available, then take payment, then decrement."""
import time

from shop import cache, store


def place_order(isbn, qty, use_cache=True):
    if cache.available(isbn, use_cache) < qty:     # CHECK
        return False
    time.sleep(0.01)                               # payment authorisation happens here
    store.decrement(isbn, qty)                     # ACT
    return True
