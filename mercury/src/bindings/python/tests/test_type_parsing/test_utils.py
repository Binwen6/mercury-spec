import unittest

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.type_parsing.utils import check_pairs


class TestBraceMatching(unittest.TestCase):
    
    def test_valid_braces(self):
        self.assertTrue(check_pairs("()"))
        self.assertTrue(check_pairs("([])"))
        self.assertTrue(check_pairs("({})"))

    def test_invalid_braces(self):
        self.assertFalse(check_pairs("{{}"))
        self.assertFalse(check_pairs("({)}"))
        self.assertFalse(check_pairs("[{)]"))


if __name__ == '__main__':
    unittest.main()
