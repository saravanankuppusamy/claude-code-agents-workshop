"""Inventory management for Tidewater Books (deliberately imperfect)."""
import json

MaxStock = 500          # naming: constant should be MAX_STOCK


def LoadInventory(path):  # naming: should be load_inventory
    f = open(path)      # no context manager, no error handling
    data = json.load(f)
    return data


def restock(inv, isbn, qty):
    # tpyo in this comment is the "bug" we ask the reviewer to fix
    current = inv.get(isbn, 0)
    if current + qty > MaxStock:
        qty = MaxStock - current
    inv[isbn] = current + qty
    return inv
