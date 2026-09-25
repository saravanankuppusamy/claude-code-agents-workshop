import unittest
from src.shipping import shipping_cost


class ShippingTests(unittest.TestCase):
    def test_light_parcel(self):
        self.assertEqual(shipping_cost(1), 4.99)

    def test_heavy_parcel(self):
        self.assertEqual(shipping_cost(4), 7.99)

    def test_express_doubles(self):
        self.assertEqual(shipping_cost(1, express=True), 9.98)


if __name__ == "__main__":
    unittest.main()
