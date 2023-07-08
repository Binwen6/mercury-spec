class TestCheckFilterSyntax(unittest.TestCase):
    # ... existing test methods ...

    def test_valid_dict_with_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dict filter="none"></dict>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_dict_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dict filter="none">
                           <named-field name="field1">
                               <string filter="equals">value1</string>
                           </named-field>
                       </dict>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_list_with_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <list filter="none"></list>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_list_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <list filter="none">
                           <string filter="equals">value1</string>
                       </list>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_string_with_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <string filter="none"></string>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_string_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <string filter="none">value1</string>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_type_declaration_with_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-declaration filter="none"></type-declaration>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_declaration_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-declaration filter="none">
                           <type-string filter="equals">value1</type-string>
                       </type-declaration>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)
