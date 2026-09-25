"""Tiny JSON-file stock store (stands in for a database without row locks)."""
import json
import os
import tempfile
import time

PATH = os.environ.get("SHOP_STOCK", "stock.json")


def read_stock(isbn):
    with open(PATH) as f:
        return json.load(f).get(isbn, 0)


def write_stock(isbn, value):
    with open(PATH) as f:
        data = json.load(f)
    data[isbn] = value
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(PATH)), suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)
    os.replace(tmp, PATH)               # each write is atomic... the read-modify-write is not


def decrement(isbn, qty):
    current = read_stock(isbn)          # read
    time.sleep(0.002)                   # simulated DB latency
    write_stock(isbn, current - qty)    # write (no floor at zero, no lock)
