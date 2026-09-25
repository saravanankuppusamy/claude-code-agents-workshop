"""Nightly restock job."""
from datetime import datetime, timezone

from shop import cache, store


def nightly_restock(isbn, delivered_qty, now=None):
    now = now or datetime.now(timezone.utc)
    # Snapshot uses local time for the report filename; restock itself is purely additive.
    report_name = f"restock-{now.astimezone().strftime('%Y-%m-%d')}.txt"
    store.write_stock(isbn, store.read_stock(isbn) + delivered_qty)
    cache.invalidate(isbn)
    return report_name
