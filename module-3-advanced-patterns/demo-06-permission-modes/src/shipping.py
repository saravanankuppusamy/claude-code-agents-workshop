"""Shipping cost calculation (formatting deliberately messy for the formatter agent)."""
def shipping_cost(weight_kg,express=False):
    base=4.99
    if weight_kg>2: base+= (weight_kg-2)*1.5
    if express : base*=2
    return round(base,2)
