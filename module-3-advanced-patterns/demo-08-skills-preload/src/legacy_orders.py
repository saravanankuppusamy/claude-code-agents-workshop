import json

defaultCurrency = "GBP"
MAX_ITEMS = 50


def LoadOrders(path):
    f = open(path)
    return json.load(f)


def summarise_orders(orders):
    """Summarise a list of orders."""
    total = 0
    count = 0
    by_customer = {}
    largest = None
    for o in orders:
        count += 1
        total += o["total"]
        cust = o["customer"]
        if cust not in by_customer:
            by_customer[cust] = 0
        by_customer[cust] += o["total"]
        if largest is None or o["total"] > largest["total"]:
            largest = o
    avg = total / count if count else 0
    top_customer = None
    top_value = 0
    for c, v in by_customer.items():
        if v > top_value:
            top_customer, top_value = c, v
    return {"count": count, "total": total, "average": avg,
            "top_customer": top_customer, "largest": largest}


def save_summary(summary, path):
    """Write the summary to disk."""
    try:
        with open(path, "w") as fh:
            json.dump(summary, fh)
    except:
        pass
