import mercury_nn as mc
from mercury_nn import filter_validation

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config import Config

import unittest
from lxml import etree as ET
import yaml


class TestFiltersValidity(unittest.TestCase):
    
    def testBaseModelSyntacticalValidity(self):
        base_model_element = ET.parse(Config.baseModelFilterPath).getroot()
        self.assertTrue(filter_validation.checkFilterSyntax(base_model_element).isValid)
    
    def testCallSchemesSyntacticalValidity(self):
        """Checks that metadata & call scheme files are present and that the syntax of each call scheme is valid
        """
        with open(Config.callSchemesMetadataPath, 'r') as f:
            metadata = yaml.safe_load(f)
        
        for key, value in metadata.items():
            # key is name of the call scheme and value is the file path
            filepath = Config.callSchemesRootDir.joinpath(value)

            filter_element = ET.parse(filepath).getroot()
            self.assertTrue(filter_validation.checkFilterSyntax(filter_element).isValid)
    

if __name__ == '__main__':
    unittest.main()
    