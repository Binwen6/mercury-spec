import unittest
import xml.etree.ElementTree as ET

import logging

logging.basicConfig(level=logging.INFO)

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import src as mc


class TestModelCreation(unittest.TestCase):
    
    def test_chatapi_creation(self):
        all_available_models = mc.enumerateAvailableModels()
        filterObject = mc.Filter.fromArgs(modelType='chat-completion')

        chat_model = all_available_models.select(filterObject=filterObject)[0]
        self.assertEqual(mc.MetadataUtils.getModelName(chat_model.metadata), 'ChatGPT-cloud')

        chat_api = mc.instantiateModel(chat_model)
        self.assertEqual(
            mc.utils.dictElementToDict(
                mc.utils.dictElementToDict(chat_api.metadata)['header'])['name'].text,
            'ChatGPT-cloud')

        response = chat_api.call(inputs=[
            ("What is the product of 121 and 11? Output the NUMBER ONLY and NOTHING ELSE.", True),
        ])
        
        logging.info(f'AI response: {response}')

        self.assertEqual(response, '1331')

if __name__ == '__main__':
    unittest.main()
