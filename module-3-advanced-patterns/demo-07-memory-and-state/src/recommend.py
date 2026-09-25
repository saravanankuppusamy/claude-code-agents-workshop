"""Recommendations (work stream: 'readers also bought')."""
def also_bought(orders, isbn, top=3):
    counts = {}
    for order in orders:
        if isbn in order:
            for other in order:
                if other != isbn:
                    counts[other] = counts.get(other, 0) + 1
    return sorted(counts, key=counts.get, reverse=True)[:top]
