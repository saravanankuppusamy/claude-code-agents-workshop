def add_item(cart, isbn, qty=1):
    cart[isbn] = cart.get(isbn, 0) + qty
    return cart

def remove_item(cart, isbn):
    cart.pop(isbn, None)
    return cart

def cart_total(cart, price_lookup, is_member=False):
    total = sum(price_lookup(i) * q for i, q in cart.items())
    return round(total * (0.9 if is_member else 1), 2)
