import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent.parent.joinpath('bindings/python')))

from config import Config
from src.mercury_nn.validation import filter_validation

import unittest
from lxml import etree as ET
import yaml


class TestFiltersValidity(unittest.TestCase):
    
    def testBaseModelSyntacticalValidity(self):
        base_model_element = ET.parse(Config.baseModelFilterPath).getroot()
        self.assertTrue(filter_validation.checkFilterSyntax(base_model_element).isValid)
    
    def testCallSchemesSyntacticalValidity(self):
        """Checks that metadata & tag files are present and that the filter syntax of each tag is valid
        """
        with open(Config.tagsMetadataPath, 'r') as f:
            metadata = yaml.safe_load(f)
        
        for key, value in metadata.items():
            # key is name of the call scheme and value is the file path
            filepath = Config.tagsRootDir.joinpath(value)

            filter_element = ET.parse(filepath).getroot()
            self.assertEqual(filter_validation.checkFilterSyntax(filter_element), filter_validation.SyntaxValidationResult.valid())
    

if __name__ == '__main__':
    unittest.main()
    