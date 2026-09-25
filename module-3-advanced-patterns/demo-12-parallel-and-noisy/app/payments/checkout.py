"""Checkout flow."""
from app.auth.middleware import require_login
from app.payments.charge import charge


def checkout(request, gateway, cart):
    require_login(request)                         # may raise mid-checkout after 15 min
    order_id = cart.order_id
    return charge(gateway, order_id, cart.total)
