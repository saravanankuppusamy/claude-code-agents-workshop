"""Order placement."""
from tidewater import cart, storage, notify

def place_order(customer_id, items, is_member=False):
    total = cart.cart_total(items, is_member)
    orders = storage.load("orders")
    order_id = len(orders) + 1
    orders[order_id] = {"customer": customer_id, "items": items, "total": total}
    storage.save("orders", orders)
    notify.send_receipt(customer_id, order_id, total)
    return order_id
