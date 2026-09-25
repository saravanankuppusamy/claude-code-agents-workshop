"""Pricing rules."""
MEMBER_DISCOUNT = 0.10

def price_with_discount(list_price, is_member):
    return round(list_price * (1 - MEMBER_DISCOUNT), 2) if is_member else list_price
