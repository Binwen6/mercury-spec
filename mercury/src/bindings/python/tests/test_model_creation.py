import unittest
import xml.etree.ElementTree as ET

import logging

logging.basicConfig(level=logging.INFO)

import sys
sys.path.append('..')

import src as mc


class TestModelCreation(unittest.TestCase):
    
    def test_chatapi_creation(self):
        all_available_models = mc.enumerateAvailableModels()
        filterElement = ET.fromstring(
"""<?xml version="1.0" encoding="UTF-8"?>
<dict filter="all">
    <named-field name="metadata">
        <dict filter="all">
            <named-field name="class">
                <string filter="equals">chat-completion</string>
            </named-field>
        </dict>
    </named-field>
</dict>
"""
        )

        chat_model = all_available_models.select(filterElement=filterElement)[0]
        self.assertEqual(mc.ManifestUtils.getModelName(chat_model.manifestData), 'ChatGPT-cloud')

        chat_api = mc.instantiateModel(chat_model)
        self.assertEqual(
            mc.utils.dictElementToDict(
                mc.utils.dictElementToDict(chat_api.metadata)['metadata'])['name'].text,
            'ChatGPT-cloud')

        response = chat_api.call(inputs=[
            ("What is the product of 121 and 11? Output the NUMBER ONLY and NOTHING ELSE.", True),
        ])
        
        logging.info(f'AI response: {response}')

        self.assertEqual(response, '1331')

if __name__ == '__main__':
    unittest.main()
