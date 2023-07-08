# code in this file are authored by ChatGPT and finetuned by Trent Fellbootman
import unittest
import xml.etree.ElementTree as ET
from enum import Enum

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.manifest_validation import checkSyntax, checkTypeDeclarationSyntax, checkFilterSyntax, checkTypeDeclarationFilterSyntax


class TestCheckSyntax(unittest.TestCase):
    def test_checkSyntax_validDict(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <dict>
                        <named-field name="field1">
                            <string>value1</string>
                        </named-field>
                        <named-field name="field2">
                            <string>value2</string>
                        </named-field>
                    </dict>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertTrue(result)

    def test_checkSyntax_invalidDict_invalidTag(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <dict>
                        <named-field name="field1">
                            <string>value1</string>
                        </named-field>
                        <named-field name="field2">
                            <string>value2</string>
                        </named-field>
                        <invalid-tag>Invalid</invalid-tag>
                    </dict>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertFalse(result)

    def test_checkSyntax_invalidDict_duplicateNames(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <dict>
                        <named-field name="field1">
                            <string>value1</string>
                        </named-field>
                        <named-field name="field1">
                            <string>value2</string>
                        </named-field>
                    </dict>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertFalse(result)

    def test_checkSyntax_validList(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <list>
                        <string>value1</string>
                        <string>value2</string>
                    </list>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertTrue(result)

    def test_checkSyntax_invalidList_invalidChild(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <list>
                        <string>value1</string>
                        <invalid-child>Invalid</invalid-child>
                    </list>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertFalse(result)

    def test_checkSyntax_validNamedField(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <named-field name="field1">
                        <string>value1</string>
                    </named-field>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertTrue(result)

    def test_checkSyntax_invalidNamedField_missingName(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <named-field>
                        <string>value1</string>
                    </named-field>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertFalse(result)

    def test_checkSyntax_invalidNamedField_invalidChildrenCount(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <named-field name="field1">
                        <string>value1</string>
                        <string>value2</string>
                    </named-field>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertFalse(result)

    def test_checkSyntax_validString(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <string>value1</string>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertTrue(result)

    def test_checkSyntax_invalidString_invalidChild(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <string>
                        <invalid-child>Invalid</invalid-child>
                    </string>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertFalse(result)

    def test_checkSyntax_validTypeIdentifier(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-declaration>
                        <type-string></type-string>
                    </type-declaration>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertTrue(result)

    def test_checkSyntax_invalidTypeIdentifier_invalidChildrenCount(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-declaration></type-declaration>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertFalse(result)


class TestCheckTypeDeclarationSyntax(unittest.TestCase):
    def test_checkTypeDeclarationSyntax_validString(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-string></type-string>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result)

    def test_checkTypeDeclarationSyntax_invalidString_invalidChild(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-string>
                        <invalid-child>Invalid</invalid-child>
                    </type-string>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)

    def test_checkTypeDeclarationSyntax_validTensor(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-tensor>
                        <dim>3</dim>
                        <dim>4</dim>
                    </type-tensor>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result)

    def test_checkTypeDeclarationSyntax_invalidTensor_invalidChild(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-tensor>
                        <invalid-child>Invalid</invalid-child>
                    </type-tensor>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)

    def test_checkTypeDeclarationSyntax_validList(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-list>
                        <type-string></type-string>
                    </type-list>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result)

    def test_checkTypeDeclarationSyntax_invalidList_invalidChildrenCount_NotEnough(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-list></type-list>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)
    
    def test_checkTypeDeclarationSyntax_invalidList_invalidChildrenCount_TooMany(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-list><type-string/><type-string/></type-list>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)

    def test_checkTypeDeclarationSyntax_validTuple(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-tuple>
                        <type-string></type-string>
                        <type-tensor>
                            <dim>3</dim>
                        </type-tensor>
                    </type-tuple>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result)

    def test_checkTypeDeclarationSyntax_invalidTuple_invalidChild(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-tuple>
                        <type-string></type-string>
                        <invalid-child>Invalid</invalid-child>
                    </type-tuple>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)

    def test_checkTypeDeclarationSyntax_validNamedValueCollection(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-named-value-collection>
                        <type-named-value name="field1"><type-string/></type-named-value>
                        <type-named-value name="field2"><type-string/></type-named-value>
                    </type-named-value-collection>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result)

    def test_checkTypeDeclarationSyntax_invalidNamedValueCollection_invalidTag(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-named-value-collection>
                        <type-named-value name="field1"><type-string/></type-named-value>
                        <type-named-value name="field2"><type-string/></type-named-value>
                        <invalid-tag>Invalid</invalid-tag>
                    </type-named-value-collection>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)

    def test_checkTypeDeclarationSyntax_invalidNamedValueCollection_duplicateNames(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-named-value-collection>
                        <type-named-value name="field1"><type-string/></type-named-value>
                        <type-named-value name="field1"><type-string/></type-named-value>
                    </type-named-value-collection>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)

    def test_checkTypeDeclarationSyntax_validNamedValue(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-named-value name="field1"><type-string/></type-named-value>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result)

    def test_checkTypeDeclarationSyntax_invalidNamedValue_missingName(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-named-value><type-string/></type-named-value>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)

    def test_checkTypeDeclarationSyntax_invalidNamedValue_invalidContent(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-named-value name="field1">
                        <invalid-child>Invalid</invalid-child>
                    </type-named-value>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)
    
    def test_checkTypeDeclarationSyntax_invalidNamedValue_NotEnoughChildren(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-named-value name="field1">
                    </type-named-value>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)
    
    def test_checkTypeDeclarationSyntax_invalidNamedValue_TooManyChildren(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <type-named-value name="field1">
                        <type-string/>
                        <type-string/>
                    </type-named-value>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)

    def test_checkTypeDeclarationSyntax_validDim(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <dim>3</dim>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result)

    def test_checkTypeDeclarationSyntax_invalidDim_invalidContent(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <dim>Invalid</dim>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)

    def test_checkTypeDeclarationSyntax_invalidTag(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <invalid-tag>Invalid</invalid-tag>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertFalse(result)


class TestCheckFilterSyntax(unittest.TestCase):
    def test_valid_dict_with_all_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dict filter="all">
                           <named-field name="field1">
                               <string filter="equals">value1</string>
                           </named-field>
                           <named-field name="field2">
                               <string filter="equals">value2</string>
                           </named-field>
                       </dict>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_dict_with_missing_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dict>
                           <named-field name="field1">
                               <string filter="equals">value1</string>
                           </named-field>
                           <named-field name="field2">
                               <string filter="equals">value2</string>
                           </named-field>
                       </dict>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)

    def test_invalid_dict_with_invalid_filter_operation_type(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dict filter="invalid_operation">
                           <named-field name="field1">
                               <string filter="equals">value1</string>
                           </named-field>
                           <named-field name="field2">
                               <string filter="equals">value2</string>
                           </named-field>
                       </dict>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_list_with_all_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <list filter="all">
                           <dict filter="all">
                               <named-field name="field1">
                                   <string filter="equals">value1</string>
                               </named-field>
                           </dict>
                           <string filter="equals">value2</string>
                       </list>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_list_with_missing_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <list>
                           <dict filter="all">
                               <named-field name="field1">
                                   <string filter="equals">value1</string>
                               </named-field>
                           </dict>
                           <string filter="equals">value2</string>
                       </list>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)

    def test_invalid_list_with_invalid_filter_operation_type(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <list filter="invalid_operation">
                           <dict filter="all">
                               <named-field name="field1">
                                   <string filter="equals">value1</string>
                               </named-field>
                           </dict>
                           <string filter="equals">value2</string>
                       </list>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_named_field_with_all_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <named-field name="field1">
                           <string filter="equals">value1</string>
                       </named-field>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_named_field_missing_name_attribute(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <named-field>
                           <string filter="equals">value1</string>
                       </named-field>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)

    def test_invalid_named_field_missing_child_element(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <named-field name="field1"></named-field>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_string_with_equals_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <string filter="equals">value1</string>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_string_with_excess_child_element(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <string filter="equals">value1
                           <child>child element</child>
                       </string>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_type_identifier_with_type_match_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-declaration filter="type-match">
                           <type-string/>
                       </type-declaration>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_identifier_with_no_child_element(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-declaration filter="type-match"></type-declaration>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertFalse(result)
    
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


class TestCheckTypeDeclarationFilterSyntax(unittest.TestCase):
    def test_valid_type_string_with_no_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-string></type-string>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)

    def test_valid_type_tensor_with_all_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-tensor filter="all">
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_tensor_with_missing_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-tensor>
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_invalid_type_tensor_with_invalid_filter_operation_type(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-tensor filter="invalid_operation">
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_type_tuple_with_all_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-tuple filter="all">
                           <type-string/>
                           <type-string/>
                       </type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_tuple_with_missing_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-tuple>
                           <type-string/>
                           <type-string/>
                       </type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_invalid_type_tuple_with_invalid_filter_operation_type(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-tuple filter="invalid_operation">
                           <type-string/>
                           <type-string/>
                       </type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_type_named_value_collection_with_all_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-named-value-collection filter="all">
                           <type-named-value name="name1">
                               <type-string/>
                           </type-named-value>
                           <type-named-value name="name2">
                               <type-string/>
                           </type-named-value>
                       </type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)
    
    def test_invalid_type_named_value_collection_with_duplicate_names(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-named-value-collection filter="all">
                           <type-named-value name="name1">
                               <type-string/>
                           </type-named-value>
                           <type-named-value name="name1">
                               <type-string/>
                           </type-named-value>
                       </type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_invalid_type_named_value_collection_with_missing_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-named-value-collection>
                           <type-named-value name="name1">
                               <type-string/>
                           </type-named-value>
                           <type-named-value name="name2">
                               <type-string/>
                           </type-named-value>
                       </type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_invalid_type_named_value_collection_with_invalid_filter_operation_type(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-named-value-collection filter="invalid_operation">
                           <type-named-value name="name1">
                               <type-string/>
                           </type-named-value>
                           <type-named-value name="name2">
                               <type-string/>
                           </type-named-value>
                       </type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_type_named_value_with_no_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-named-value name="name1">
                           <type-string/>
                       </type-named-value>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_named_value_missing_name_attribute(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-named-value>
                           <type-string/>
                       </type-named-value>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_invalid_type_named_value_excess_child_element(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-named-value name="name1">
                           <type-string/>
                           <type-string/>
                       </type-named-value>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_type_dim_with_equals_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dim filter="equals">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)
    
    def test_valid_type_dim_with_greater_than_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dim filter="gt">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)
    
    def test_valid_type_dim_with_greater_than_or_equals_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dim filter="ge">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)
    
    def test_valid_type_dim_with_less_than_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dim filter="lt">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)
    
    def test_valid_type_dim_with_less_than_or_equals_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dim filter="le">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_dim_with_missing_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dim></dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_invalid_type_dim_with_invalid_filter_operation_type(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dim filter="invalid_operation">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_invalid_type_dim_with_non_integer_text_content(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dim filter="gt">not_an_integer</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)
    
    def test_valid_type_tensor_with_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-tensor filter="none"></type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_tensor_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-tensor filter="none">
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_type_list_with_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-list filter="none"></type-list>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_list_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-list filter="none">
                           <type-string/>
                       </type-list>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_type_tuple_with_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-tuple filter="none"></type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_tuple_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-tuple filter="none">
                           <type-string/>
                       </type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_type_named_value_collection_with_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-named-value-collection filter="none"></type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_named_value_collection_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <type-named-value-collection filter="none">
                           <type-named-value name="name1">
                               <type-string/>
                           </type-named-value>
                       </type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)

    def test_valid_type_dim_with_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dim filter="none"/>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result)

    def test_invalid_type_dim_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''<?xml version="1.0" encoding="UTF-8"?>
                       <dim filter="none">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
