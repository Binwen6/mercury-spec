import unittest

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import src.mercury_nn as mc

import sys
import os

from src.mercury_nn.specification.interface import ManifestUtils


class TestEnumerateModels(unittest.TestCase):
    
    def test_enumerateModels(self):
        all_available_models = mc.enumerateAvailableModels()
        model_names = set(ManifestUtils.getModelName(entry.manifest) for entry in all_available_models)
        self.assertEqual(model_names, {'DALL E', 'ChatGPT-cloud'})


class TestModelCollectionMethods(unittest.TestCase):
    
    def setUp(self):
        self.all_available_models = mc.enumerateAvailableModels()
    
    def test_model_entries_properties(self):
        model_names = set(ManifestUtils.getModelName(entry.manifest) for entry in self.all_available_models)
        self.assertEqual(model_names, {'DALL E', 'ChatGPT-cloud'})
        
    def test_select_all_match(self):
        filterElement = mc.Filter.fromArgs()
        
        model_names = set(ManifestUtils.getModelName(entry.manifest) for entry in self.all_available_models.select(filterElement))
        self.assertEqual(model_names, {'DALL E', 'ChatGPT-cloud'})
    
    def test_select_none_match(self):
        filterElement = mc.Filter.fromArgs(callSchemes=['text-continuation'])
        
        model_names = set(ManifestUtils.getModelName(entry.manifest) for entry in self.all_available_models.select(filterElement))
        self.assertEqual(model_names, set())
    
    def test_select_some_match(self):
        filterElement = mc.Filter.fromArgs(callSchemes=['image-generation'])
        
        model_names = set(ManifestUtils.getModelName(entry.manifest) for entry in self.all_available_models.select(filterElement))
        self.assertEqual(model_names, {'DALL E'})


if __name__ == '__main__':
    unittest.main()
