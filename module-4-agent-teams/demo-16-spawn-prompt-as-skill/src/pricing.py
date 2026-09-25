MEMBER_DISCOUNT = 0.10
GIFT_WRAP_FEE = 2.50


def member_price(price):
    return round(price * (1 - MEMBER_DISCOUNT), 2)


def gift_wrap_total(price, wrapped):
    return round(price + (GIFT_WRAP_FEE if wrapped else 0), 2)


def bulk_discount(price, qty):
    if qty >= 10:
        return round(price * qty * 0.85, 2)
    return round(price * qty, 2)
