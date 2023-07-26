import unittest

import yaml

import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().resolve().parent.parent.parent))

from src.mercury_nn.specification.load_tags import loadTags
from src.mercury_nn.config import Config


class TestLoadTags(unittest.TestCase):
    def test_loadTags(self):
        with open(Config.tagsMetadataPath, 'r') as f:
            metadata = yaml.safe_load(f)
        
        self.assertEqual(set(loadTags().keys()), set(metadata.keys()))


if __name__ == '__main__':
    unittest.main()