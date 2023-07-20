import unittest

import yaml

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mercury_nn.specification.load_call_schemes import loadCallSchemes
from src.mercury_nn.config import Config


class TestLoadCallSchemes(unittest.TestCase):
    def test_loadCallSchemes(self):
        with open(Config.callSchemesMetadataPath, 'r') as f:
            metadata = yaml.safe_load(f)
        
        self.assertEqual(set(loadCallSchemes().keys()), set(metadata.keys()))


if __name__ == '__main__':
    unittest.main()