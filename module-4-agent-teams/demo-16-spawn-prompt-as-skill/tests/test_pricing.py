import unittest
from src.pricing import member_price


class PricingTests(unittest.TestCase):
    def test_member_price(self):
        self.assertEqual(member_price(10.0), 9.0)


if __name__ == "__main__":
    unittest.main()
