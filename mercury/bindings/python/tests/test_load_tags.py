import unittest

import yaml

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mercury_nn.specification.load_tags import loadTags
from src.mercury_nn.config import Config


class TestLoadTags(unittest.TestCase):
    def test_loadTags(self):
        with open(Config.tagsMetadataPath, 'r') as f:
            metadata = yaml.safe_load(f)
        
        self.assertEqual(set(loadTags().keys()), set(metadata.keys()))


if __name__ == '__main__':
    unittest.main()