# code in this file are authored by ChatGPT and finetuned by Trent Fellbootman
import unittest
from lxml import etree as ET
from enum import Enum

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mercury.filter_validation import (
    checkFilterSyntax, checkTypeDeclarationFilterSyntax, SyntaxValidationResult, FilterSyntaxInvalidityType
)


# convenient classes
_InvalidityInfo = SyntaxValidationResult.InvalidityInfo
_InvalidityTypes = FilterSyntaxInvalidityType
_InvalidityPosition = SyntaxValidationResult.InvalidityInfo.InvalidityPosition

class TestSyntaxValidationResult(unittest.TestCase):
    
    def test_InvalidityPosition(self):
        a = _InvalidityPosition(1)
        b = _InvalidityPosition(1)
        self.assertEqual(a, b)

        a = _InvalidityPosition(1)
        b = _InvalidityPosition(2)
        self.assertNotEqual(a, b)
    
    def test_InvalidityInfo(self):
        a = _InvalidityInfo(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(1)
        )

        b = _InvalidityInfo(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(1)
        )

        self.assertEqual(a, b)

        a = _InvalidityInfo(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(1)
        )

        b = _InvalidityInfo(
            invalidityType=_InvalidityTypes.DICT_DUPLICATE_KEYS,
            invalidityPosition=_InvalidityPosition(1)
        )

        self.assertNotEqual(a, b)

        a = _InvalidityInfo(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(1)
        )

        b = _InvalidityInfo(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(2)
        )

        self.assertNotEqual(a, b)
    
    def test_SyntaxValidationResult(self):
        a = SyntaxValidationResult.valid()
        b = SyntaxValidationResult.valid()
        self.assertEqual(a, b)

        a = SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(1)
        )

        b = SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(1)
        )

        self.assertEqual(a, b)

        a = SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(1)
        )

        b = SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.NAMED_FIELD_INCORRECT_CHILDREN_COUNT,
            invalidityPosition=_InvalidityPosition(1)
        )

        self.assertNotEqual(a, b)
        
        a = SyntaxValidationResult.valid()

        b = SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(1)
        )

        self.assertNotEqual(a, b)

class TestCheckFilterSyntax(unittest.TestCase):
    def test_valid_dict_with_all_filter_operation(self):
        xml_string = '''
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
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_dict_with_missing_filter_operation(self):
        xml_string = '''
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
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_dict_with_invalid_filter_operation_type(self):
        xml_string = '''
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
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_list_with_all_filter_operation(self):
        xml_string = '''
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
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_list_with_missing_filter_operation(self):
        xml_string = '''
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
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_list_with_invalid_filter_operation_type(self):
        xml_string = '''
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
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_named_field_with_all_filter_operation(self):
        xml_string = '''
                       <named-field name="field1">
                           <string filter="equals">value1</string>
                       </named-field>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_named_field_missing_name_attribute(self):
        xml_string = '''
                       <named-field>
                           <string filter="equals">value1</string>
                       </named-field>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.NAMED_FIELD_MISSING_NAME_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_named_field_missing_child_element(self):
        xml_string = '''
                       <named-field name="field1"></named-field>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.NAMED_FIELD_INCORRECT_CHILDREN_COUNT,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_string_with_equals_filter_operation(self):
        xml_string = '''
                       <string filter="equals">value1</string>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_string_with_excess_child_element(self):
        xml_string = '''
                       <string filter="equals">value1
                           <child>child element</child>
                       </string>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.STRING_ILLEGAL_CHILD,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_identifier_with_type_match_filter_operation(self):
        xml_string = '''
                       <type-declaration filter="type-match">
                           <type-string/>
                       </type-declaration>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_identifier_with_no_child_element(self):
        xml_string = '''
                       <type-declaration filter="type-match"></type-declaration>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_INCORRECT_CHILD_COUNT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_valid_dict_with_none_filter_operation(self):
        xml_string = '''
                       <dict filter="none"></dict>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_dict_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <dict filter="none">
                           <named-field name="field1">
                               <string filter="equals">value1</string>
                           </named-field>
                       </dict>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_list_with_none_filter_operation(self):
        xml_string = '''
                       <list filter="none"></list>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_list_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <list filter="none">
                           <string filter="equals">value1</string>
                       </list>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_string_with_none_filter_operation(self):
        xml_string = '''
                       <string filter="none"></string>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_string_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <string filter="none">value1</string>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_declaration_with_none_filter_operation(self):
        xml_string = '''
                       <type-declaration filter="none"></type-declaration>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_declaration_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <type-declaration filter="none">
                           <type-string filter="equals">value1</type-string>
                       </type-declaration>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))


class TestCheckTypeDeclarationFilterSyntax(unittest.TestCase):
    def test_valid_type_string_with_no_filter_operation(self):
        xml_string = '''
                       <type-string></type-string>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_valid_type_tensor_with_all_filter_operation(self):
        xml_string = '''
                       <type-tensor filter="all">
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_tensor_with_missing_filter_operation(self):
        xml_string = '''
                       <type-tensor>
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_type_tensor_with_invalid_filter_operation_type(self):
        xml_string = '''
                       <type-tensor filter="invalid_operation">
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_tuple_with_all_filter_operation(self):
        xml_string = '''
                       <type-tuple filter="all">
                           <type-string/>
                           <type-string/>
                       </type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_tuple_with_missing_filter_operation(self):
        xml_string = '''
                       <type-tuple>
                           <type-string/>
                           <type-string/>
                       </type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_type_tuple_with_invalid_filter_operation_type(self):
        xml_string = '''
                       <type-tuple filter="invalid_operation">
                           <type-string/>
                           <type-string/>
                       </type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_named_value_collection_with_all_filter_operation(self):
        xml_string = '''
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
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_invalid_type_named_value_collection_with_duplicate_names(self):
        xml_string = '''
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
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_type_named_value_collection_with_missing_filter_operation(self):
        xml_string = '''
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
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_type_named_value_collection_with_invalid_filter_operation_type(self):
        xml_string = '''
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
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_named_value_with_no_filter_operation(self):
        xml_string = '''
                       <type-named-value name="name1">
                           <type-string/>
                       </type-named-value>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_named_value_missing_name_attribute(self):
        xml_string = '''
                       <type-named-value>
                           <type-string/>
                       </type-named-value>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_MISSING_NAME_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_type_named_value_excess_child_element(self):
        xml_string = '''
                       <type-named-value name="name1">
                           <type-string/>
                           <type-string/>
                       </type-named-value>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_INCORRECT_CHILDREN_COUNT,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_dim_with_equals_filter_operation(self):
        xml_string = '''
                       <dim filter="equals">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_valid_type_dim_with_greater_than_filter_operation(self):
        xml_string = '''
                       <dim filter="gt">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_valid_type_dim_with_greater_than_or_equals_filter_operation(self):
        xml_string = '''
                       <dim filter="ge">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_valid_type_dim_with_less_than_filter_operation(self):
        xml_string = '''
                       <dim filter="lt">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_valid_type_dim_with_less_than_or_equals_filter_operation(self):
        xml_string = '''
                       <dim filter="le">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_dim_with_missing_filter_operation(self):
        xml_string = '''
                       <dim></dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_type_dim_with_invalid_filter_operation_type(self):
        xml_string = '''
                       <dim filter="invalid_operation">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_type_dim_with_non_integer_text_content(self):
        xml_string = '''
                       <dim filter="gt">not_an_integer</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_valid_type_tensor_with_none_filter_operation(self):
        xml_string = '''
                       <type-tensor filter="none"></type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_tensor_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <type-tensor filter="none">
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_list_with_none_filter_operation(self):
        xml_string = '''
                       <type-list filter="none"></type-list>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_list_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <type-list filter="none">
                           <type-string/>
                       </type-list>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_tuple_with_none_filter_operation(self):
        xml_string = '''
                       <type-tuple filter="none"></type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_tuple_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <type-tuple filter="none">
                           <type-string/>
                       </type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_named_value_collection_with_none_filter_operation(self):
        xml_string = '''
                       <type-named-value-collection filter="none"></type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_named_value_collection_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <type-named-value-collection filter="none">
                           <type-named-value name="name1">
                               <type-string/>
                           </type-named-value>
                       </type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_dim_with_none_filter_operation(self):
        xml_string = '''
                       <dim filter="none"/>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_dim_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <dim filter="none">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkTypeDeclarationFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))


if __name__ == '__main__':
    unittest.main()