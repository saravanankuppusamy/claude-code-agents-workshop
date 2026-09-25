"""A deliberately NOISY suite: 400 generated tests that print a lot. Two fail."""
import unittest


def price_with_vat(net, rate=0.2):
    return round(net * (1 + rate), 2)


class BulkCatalogTests(unittest.TestCase):
    pass


def make_test(i):
    def test(self):
        for line in range(4):
            print(f"[catalog-bulk] case={i:03d} step={line} checking isbn=97800000{i:05d} net={i/7:.4f}")
        net = round(i / 7, 2)
        expected = round(net * 1.2, 2)
        if i in (137, 311):                          # two planted failures
            expected += 0.01
        self.assertEqual(price_with_vat(net), expected, f"VAT mismatch for case {i}")
    return test


for _i in range(400):
    setattr(BulkCatalogTests, f"test_case_{_i:03d}", make_test(_i))

if __name__ == "__main__":
    unittest.main()
