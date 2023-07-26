from lxml import etree as ET
import unittest
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).absolute().resolve().parent.parent.parent))

from src.mercury_nn.specification.load_base_model_filter import loadBaseModelFilter


class TestLoadBaseModelFilter(unittest.TestCase):
    
    def test_IsXMLElement(self):
        self.assertTrue(isinstance(loadBaseModelFilter(), ET._Element))


if __name__ == '__main__':
    unittest.main()
