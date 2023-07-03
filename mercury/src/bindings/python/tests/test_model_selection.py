import unittest
import xml.etree.ElementTree as ET

import sys
sys.path.append('..')

import src as mc
from src.spec_interface import ManifestUtils


class TestEnumerateModels(unittest.TestCase):
    
    def test_enumerateModels(self):
        all_available_models = mc.enumerateAvailableModels()
        model_names = set(ManifestUtils.getModelName(entry.manifestData) for entry in all_available_models)
        self.assertEqual(model_names, {'AlexNet', 'ChatGPT-cloud'})


class TestModelCollectionMethods(unittest.TestCase):
    
    def setUp(self):
        self.all_available_models = mc.enumerateAvailableModels()
    
    def test_model_entries_properties(self):
        model_names = set(ManifestUtils.getModelName(entry.manifestData) for entry in self.all_available_models)
        self.assertEqual(model_names, {'AlexNet', 'ChatGPT-cloud'})
        
    def test_select_all_match(self):
        filterElement = ET.fromstring(
"""<?xml version="1.0" encoding="UTF-8"?>
<dict filter="none"/>
"""
        )
        
        model_names = set(ManifestUtils.getModelName(entry.manifestData) for entry in self.all_available_models.select(filterElement))
        self.assertEqual(model_names, {'AlexNet', 'ChatGPT-cloud'})
    
    def test_select_none_match(self):
        filterElement = ET.fromstring(
"""<?xml version="1.0" encoding="UTF-8"?>
<dict filter="all">
    <named-field name="metadata">
        <dict filter="all">
            <named-field name="name">
                <string filter="equals">koala</string>
            </named-field>
        </dict>
    </named-field>
</dict>
"""
        )
        
        model_names = set(ManifestUtils.getModelName(entry.manifestData) for entry in self.all_available_models.select(filterElement))
        self.assertEqual(model_names, set())
    
    def test_select_some_match(self):
        filterElement = ET.fromstring(
"""<?xml version="1.0" encoding="UTF-8"?>
<dict filter="all">
    <named-field name="metadata">
        <dict filter="all">
            <named-field name="name">
                <string filter="none"></string>
            </named-field>
            <named-field name="class">
                <string filter="equals">image-classification</string>
            </named-field>
            <named-field name="description">
                <string filter="none"/>
            </named-field>
        </dict>
    </named-field>
</dict>
"""
        )
        
        model_names = set(ManifestUtils.getModelName(entry.manifestData) for entry in self.all_available_models.select(filterElement))
        self.assertEqual(model_names, {'AlexNet'})


if __name__ == '__main__':
    unittest.main()
