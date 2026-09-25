def place_order(store, customer_id, cart, total):
    orders = store.load("orders")
    order_id = max(map(int, orders), default=0) + 1
    orders[str(order_id)] = {"customer": customer_id, "items": cart, "total": total, "status": "pending"}
    store.save("orders", orders)
    return order_id

def cancel_order(store, order_id):
    orders = store.load("orders")
    orders[str(order_id)]["status"] = "cancelled"
    store.save("orders", orders)
