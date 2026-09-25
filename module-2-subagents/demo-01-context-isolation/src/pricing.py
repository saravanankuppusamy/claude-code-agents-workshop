"""Pricing helpers for Tidewater Books."""

MEMBER_DISCOUNT = 0.10


def price_with_discount(list_price: float, is_member: bool) -> float:
    if is_member:
        return round(list_price * (1 - MEMBER_DISCOUNT), 2)
    return list_price
