#!/usr/bin/env python3
"""Reproducer for BUG-212: N buyers race for the last few copies.

    python3 repro/concurrent_orders.py                    # defaults: stock 3, 12 buyers, cache on
    python3 repro/concurrent_orders.py --no-cache          # isolate H2 (cache off)
    python3 repro/concurrent_orders.py --serial            # no concurrency at all
    python3 repro/concurrent_orders.py --trials 20         # how often does it happen?

Prints final stock, orders approved and how many trials went negative.
"""
import argparse
import json
import os
import sys
import tempfile
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def trial(stock, buyers, use_cache, serial):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.environ["SHOP_STOCK"] = path
    import importlib
    from shop import store, cache, checkout
    importlib.reload(store); importlib.reload(cache); importlib.reload(checkout)
    with open(path, "w") as f:
        json.dump({"isbn-1": stock}, f)
    results = []
    if serial:
        for _ in range(buyers):
            results.append(checkout.place_order("isbn-1", 1, use_cache))
    else:
        start = threading.Barrier(buyers)

        def buy():
            start.wait()
            results.append(checkout.place_order("isbn-1", 1, use_cache))
        threads = [threading.Thread(target=buy) for _ in range(buyers)]
        [t.start() for t in threads]
        [t.join() for t in threads]
    final = store.read_stock("isbn-1")
    os.remove(path)
    return final, sum(results)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stock", type=int, default=3)
    ap.add_argument("--buyers", type=int, default=12)
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--serial", action="store_true")
    a = ap.parse_args()
    negative = lost_updates = 0
    for _ in range(a.trials):
        final, approved = trial(a.stock, a.buyers, not a.no_cache, a.serial)
        if final < 0:
            negative += 1
        if final != a.stock - approved:
            lost_updates += 1
    mode = "serial" if a.serial else "concurrent"
    print(f"{mode}, cache={'off' if a.no_cache else 'on'}, stock={a.stock}, buyers={a.buyers}, trials={a.trials}")
    print(f"  trials ending with NEGATIVE stock : {negative}/{a.trials}")
    print(f"  trials with LOST UPDATES          : {lost_updates}/{a.trials}  (final != start - approved)")
    print(f"  last trial: final stock {final}, orders approved {approved}")


if __name__ == "__main__":
    main()
