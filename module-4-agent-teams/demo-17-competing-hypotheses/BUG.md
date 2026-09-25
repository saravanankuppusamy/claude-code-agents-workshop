# BUG-212: stock goes negative (intermittent)

- Reports page shows negative stock for popular titles a few times a week.
- Always a bestseller; never seen on slow-selling titles.
- Warehouse says "it happens after launch-day rushes".
- Someone noticed it once "right after midnight", when the nightly restock job runs.

Suspects raised in stand-up:
- **H1 – race condition** in the stock decrement (read-modify-write without a lock)
- **H2 – stale availability cache** lets checkout approve orders that no longer fit
- **H3 – restock job timezone bug** (runs at 00:00 UTC, stock snapshot taken in local time)
