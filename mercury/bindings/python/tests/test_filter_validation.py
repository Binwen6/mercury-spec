# code in this file are authored by ChatGPT and finetuned by Trent Fellbootman
import unittest
from lxml import etree as ET
from enum import Enum

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mercury_nn.validation.filter_validation import (
    checkFilterSyntax, SyntaxValidationResult, FilterSyntaxInvalidityType, FilterValidationResult, validateFilter
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
            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_valid_int_with_equals_filter_operation(self):
        xml_string = '''
                       <int filter="lt">1</int>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_invalid_int_with_invalid_literal(self):
        xml_string = '''
                       <int filter="equals">1.0</int>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INT_INVALID_INT_LITERAL,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_int_with_excess_child_element(self):
        xml_string = '''
                       <int filter="equals">value1
                           <child>child element</child>
                       </int>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_valid_float_with_equals_filter_operation(self):
        xml_string = '''
                       <float filter="gt">1</float>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
        
        xml_string = '''
                       <float filter="equals">1.5</float>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_invalid_float_with_invalid_literal(self):
        xml_string = '''
                       <float filter="equals">test</float>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.FLOAT_INVALID_FLOAT_LITERAL,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_float_with_excess_child_element(self):
        xml_string = '''
                       <float filter="equals">value1
                           <child>child element</child>
                       </float>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
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
    
    def test_valid_dict_with_no_keys(self):
        xml_string = '''
                       <dict filter="all"></dict>'''
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

    # Test type declarations
    def test_valid_type_string_with_no_filter_operation(self):
        xml_string = '''
                       <type-string></type-string>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_invalid_type_string_with_no_filter_operation(self):
        xml_string = '''
                       <type-string>test</type-string>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_valid_type_bool_with_no_filter_operation(self):
        xml_string = '''
                       <type-bool></type-bool>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_invalid_type_bool_with_illegal_content(self):
        xml_string = '''
                       <type-bool>test</type-bool>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_valid_type_int_with_no_filter_operation(self):
        xml_string = '''
                       <type-int></type-int>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_invalid_type_int_with_illegal_content(self):
        xml_string = '''
                       <type-int>test</type-int>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_valid_type_float_with_no_filter_operation(self):
        xml_string = '''
                       <type-float></type-float>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_invalid_type_float_with_illegal_content(self):
        xml_string = '''
                       <type-float>test</type-float>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_tensor_with_all_filter_operation(self):
        xml_string = '''
                       <type-tensor filter="all">
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_tensor_with_missing_filter_operation(self):
        xml_string = '''
                       <type-tensor>
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
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
        result = checkFilterSyntax(element)
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
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_tuple_with_missing_filter_operation(self):
        xml_string = '''
                       <type-tuple>
                           <type-string/>
                           <type-string/>
                       </type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
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
        result = checkFilterSyntax(element)
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
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_valid_type_named_value_collection_with_no_keys(self):
        xml_string = '''
                       <type-named-value-collection filter="all"></type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
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
        result = checkFilterSyntax(element)
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
        result = checkFilterSyntax(element)
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
        result = checkFilterSyntax(element)
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
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_named_value_missing_name_attribute(self):
        xml_string = '''
                       <type-named-value>
                           <type-string/>
                       </type-named-value>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
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
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_INCORRECT_CHILDREN_COUNT,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_dim_with_equals_filter_operation(self):
        xml_string = '''
                       <dim filter="equals">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_valid_type_dim_with_greater_than_filter_operation(self):
        xml_string = '''
                       <dim filter="gt">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_valid_type_dim_with_greater_than_or_equals_filter_operation(self):
        xml_string = '''
                       <dim filter="ge">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_valid_type_dim_with_less_than_filter_operation(self):
        xml_string = '''
                       <dim filter="lt">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_valid_type_dim_with_less_than_or_equals_filter_operation(self):
        xml_string = '''
                       <dim filter="le">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_dim_with_missing_filter_operation(self):
        xml_string = '''
                       <dim></dim>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_type_dim_with_invalid_filter_operation_type(self):
        xml_string = '''
                       <dim filter="invalid_operation">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_invalid_type_dim_with_non_integer_text_content(self):
        xml_string = '''
                       <dim filter="gt">not_an_integer</dim>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_valid_type_tensor_with_none_filter_operation(self):
        xml_string = '''
                       <type-tensor filter="none"></type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_tensor_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <type-tensor filter="none">
                           <dim filter="gt">10</dim>
                       </type-tensor>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_list_with_none_filter_operation(self):
        xml_string = '''
                       <type-list filter="none"></type-list>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_list_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <type-list filter="none">
                           <type-string/>
                       </type-list>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_tuple_with_none_filter_operation(self):
        xml_string = '''
                       <type-tuple filter="none"></type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_tuple_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <type-tuple filter="none">
                           <type-string/>
                       </type-tuple>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_named_value_collection_with_none_filter_operation(self):
        xml_string = '''
                       <type-named-value-collection filter="none"></type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_named_value_collection_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <type-named-value-collection filter="none">
                           <type-named-value name="name1">
                               <type-string/>
                           </type-named-value>
                       </type-named-value-collection>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_valid_type_dim_with_none_filter_operation(self):
        xml_string = '''
                       <dim filter="none"/>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_invalid_type_dim_with_non_empty_content_and_none_filter_operation(self):
        xml_string = '''
                       <dim filter="none">10</dim>'''
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    # Test logical operations
    def test_LogicalAnd_Valid(self):
        xml_string = '''
                        <type-tensor filter="all">
                            <logical filter="and">
                                <dim filter="gt">10</dim>
                                <dim filter="lt">15</dim>
                            </logical>
                        </type-tensor>'''
                       
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_Logical_InvalidFilterOperationType(self):
        xml_string = '''
                        <type-tensor filter="all">
                            <logical filter="all">
                                <dim filter="gt">10</dim>
                                <dim filter="lt">15</dim>
                            </logical>
                        </type-tensor>'''
                       
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(3)
        ))
    
    def test_LogicalAnd_IncorrectChildCount(self):
        xml_string = '''
                        <type-tensor filter="all">
                            <logical filter="and">
                                <dim filter="gt">10</dim>
                            </logical>
                        </type-tensor>'''
                       
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.LOGICAL_INCORRECT_CHILD_COUNT,
            invalidityPosition=_InvalidityPosition(3)
        ))
    
    def test_LogicalAnd_InvalidChild(self):
        xml_string = '''
                        <type-tensor filter="all">
                            <logical filter="and">
                                <dim filter="gt">10</dim>
                                <dim filter="invalid">15</dim>
                            </logical>
                        </type-tensor>'''
                       
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(5)
        ))
    
    def test_LogicalOr_Valid(self):
        xml_string = '''
                        <type-tensor filter="all">
                            <logical filter="or">
                                <dim filter="gt">10</dim>
                                <dim filter="lt">15</dim>
                            </logical>
                        </type-tensor>'''
                       
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_LogicalOr_IncorrectChildCount(self):
        xml_string = '''
                        <type-tensor filter="all">
                            <logical filter="or">
                                <dim filter="gt">10</dim>
                            </logical>
                        </type-tensor>'''
                       
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.LOGICAL_INCORRECT_CHILD_COUNT,
            invalidityPosition=_InvalidityPosition(3)
        ))
    
    def test_LogicalOr_InvalidChild(self):
        xml_string = '''
                        <type-tensor filter="all">
                            <logical filter="or">
                                <dim filter="gt">10</dim>
                                <dim filter="invalid">15</dim>
                            </logical>
                        </type-tensor>'''
                       
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(5)
        ))
    
    def test_LogicalNot_Valid(self):
        xml_string = '''
                        <type-tensor filter="all">
                            <logical filter="not">
                                <dim filter="gt">10</dim>
                            </logical>
                        </type-tensor>'''
                       
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_LogicalNot_IncorrectChildCount(self):
        xml_string = '''
                        <type-tensor filter="all">
                            <logical filter="not">
                                <dim filter="gt">10</dim>
                                <dim filter="gt">10</dim>
                            </logical>
                        </type-tensor>'''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.LOGICAL_INCORRECT_CHILD_COUNT,
            invalidityPosition=_InvalidityPosition(3)
        ))
    
    def test_LogicalNot_InvalidChild(self):
        xml_string = '''
                        <type-tensor filter="all">
                            <logical filter="not">
                                <dim filter="invalid">15</dim>
                            </logical>
                        </type-tensor>'''
                       
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(4)
        ))
    
    # Test tags
    def test_TagCollection_MissingFilterOperationType(self):
        xml_string = '''
        <tag-collection>
            <condensed-tags>
                koala::{
                    kangaroo,
                    monkey.bird,
                    cat::{
                        dog,
                        reptile
                    },
                },
            </condensed-tags>
        </tag-collection>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))
        
    def test_TagCollection_ExplicitMatch_ValidNonEmpty(self):
        xml_string = '''
        <tag-collection filter="explicit-tag-match">
            <condensed-tags>
                koala::{
                    kangaroo,
                    monkey.bird,
                    cat::{
                        dog,
                        reptile
                    },
                },
            </condensed-tags>
        </tag-collection>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.valid())
        
    def test_TagCollection_ExplicitMatch_ValidEmpty(self):
        xml_string = '''
        <tag-collection filter="explicit-tag-match"/>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_TagCollection_ImplicitMatch_ValidNonEmpty(self):
        xml_string = '''
        <tag-collection filter="implicit-tag-match">
            <condensed-tags>
                koala::{
                    kangaroo,
                    monkey.bird,
                    cat::{
                        dog,
                        reptile
                    },
                },
            </condensed-tags>
        </tag-collection>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.valid())
        
    def test_TagCollection_ImplicitMatch_ValidEmpty(self):
        xml_string = '''
        <tag-collection filter="implicit-tag-match"/>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_TagCollection_InvalidFilterOperation(self):
        xml_string = '''
        <tag-collection filter="all"/>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_TagCollection_ValidNone(self):
        xml_string = '''
        <tag-collection filter="none"/>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_TagCollection_InvalidNone(self):
        xml_string = '''
        <tag-collection filter="none">
            <condensed-tags>int_tag</condensed-tags>
        </tag-collection>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_TagCollection_ExplicitMatch_InvalidChildTag(self):
        xml_string = '''
        <tag-collection filter="explicit-tag-match">
            <named-field>int_tag</named-field>
        </tag-collection>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TAG_COLLECTION_INVALID_CHILD_TAG,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_TagCollection_ImplicitMatch_InvalidChildTag(self):
        xml_string = '''
        <tag-collection filter="implicit-tag-match">
            <named-field>int_tag</named-field>
        </tag-collection>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TAG_COLLECTION_INVALID_CHILD_TAG,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_Tag_IllegalEmptyContent(self):
        xml_string = '''
        <tag-collection filter="explicit-tag-match">
            <condensed-tags></condensed-tags>
        </tag-collection>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_EMPTY_CONTENT,
            invalidityPosition=_InvalidityPosition(3)
        ))
        
        xml_string = '''
        <tag-collection filter="implicit-tag-match">
            <condensed-tags/>
        </tag-collection>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_EMPTY_CONTENT,
            invalidityPosition=_InvalidityPosition(3)
        ))
    
    def test_Tag_IllegalChild(self):
        xml_string = '''
        <tag-collection filter="explicit-tag-match">
            <condensed-tags>int_tag<string>koala</string></condensed-tags>
        </tag-collection>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_CHILD,
            invalidityPosition=_InvalidityPosition(3)
        ))
    
    def test_CondensedTags_InvalidSyntax(self):
        xml_string = '''
        <tag-collection filter="explicit-tag-match">
            <condensed-tags>int:tag</condensed-tags>
        </tag-collection>
        '''
        
        element = ET.fromstring(xml_string)
        result = checkFilterSyntax(element)
        
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.CONDENSED_TAGS_INVALID_SYNTAX,
            invalidityPosition=_InvalidityPosition(3)
        ))
    
    def setUp(self):
        int_tag = ET.fromstring(
        """
        <dict filter="all">
            <named-field name="data">
                <int filter="none"/>
            </named-field>
        </dict>
        """)
        
        float_tag = ET.fromstring(
        """
        <dict filter="all">
            <named-field name="data">
                <float filter="none"/>
            </named-field>
        </dict>
        """)

        string_tag = ET.fromstring(
        """
        <dict filter="all">
            <named-field name="data">
                <string filter="none"/>
            </named-field>
        </dict>
        """)
        
        self.tag_collection = {'int_tag': int_tag, 'float_tag': float_tag, 'string_tag': string_tag}


class TestFilterValidationResult(unittest.TestCase):
    
    def test_InvalidityInfo(self):
        self.assertEqual(
            FilterValidationResult.InvalidityInfo(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(3)
                )
            ),
            FilterValidationResult.InvalidityInfo(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(3)
                )
            )
        )
        
        self.assertNotEqual(
            FilterValidationResult.InvalidityInfo(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(2)
                )
            ),
            FilterValidationResult.InvalidityInfo(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(3)
                )
            )
        )
        
        self.assertNotEqual(
            FilterValidationResult.InvalidityInfo(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(3)
                )
            ),
            FilterValidationResult.InvalidityInfo(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(3)
                )
            )
        )
    
    def test_FilterValidationResult(self):
        self.assertEqual(
            FilterValidationResult.valid(),
            FilterValidationResult.valid()
        )

        self.assertEqual(
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(3)
                )
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(3)
                )
            )
        )
        
        self.assertNotEqual(
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a'}
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a', 'b'}
            )
        )
        
        self.assertNotEqual(
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(3)
                )
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(3)
                )
            )
        )
        
        self.assertNotEqual(
            FilterValidationResult.valid(),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a'}
            ),
        )


class TestValidateFilter(unittest.TestCase):
    
    def setUp(self):
        self.tag_collection = {
            'int_tag': ET.fromstring(
            """
            <dict filter="all">
                <named-field name="data">
                    <int filter="none"/>
                </named-field>
            </dict>
            """),
            'float_tag': ET.fromstring(
            """
            <dict filter="all">
                <named-field name="data">
                    <float filter="none"/>
                </named-field>
            </dict>
            """)
        }
    
    def test_Syntax(self):
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="data">
                        <int filter="none"/>
                    </named-field>
                </dict>
                """),
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.valid()
        )
        
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="data">
                        <int/>
                    </named-field>
                </dict>
                """),
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                    invalidityType=FilterSyntaxInvalidityType.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(4)
                )
            )
        )
    
    def test_ExplicitMatch(self):
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags">
                        <tag-collection filter="explicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.valid()
        )
        
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags">
                        <tag-collection filter="explicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                            <condensed-tags>a.b</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a', 'a::b'}
            )
        )
        
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags">
                        <tag-collection filter="explicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                            <condensed-tags>test</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'test'}
            )
        )
        
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags">
                        <tag-collection filter="explicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                            <condensed-tags>test</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                tagName='test',
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.valid()
        )
        
    def test_ImplicitMatch(self):
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags">
                        <tag-collection filter="implicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.valid()
        )
        
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags">
                        <tag-collection filter="implicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                            <condensed-tags>a.b</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a', 'a::b'}
            )
        )
        
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags">
                        <tag-collection filter="implicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                            <condensed-tags>test</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'test'}
            )
        )
        
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags">
                        <tag-collection filter="implicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                            <condensed-tags>test</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                tagName='test',
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'test'}
            )
        )
    
    def test_MixedExplicitImplicit(self):
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags1">
                        <tag-collection filter="implicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                        </tag-collection>
                    </named-field>
                    
                    <named-field name="tags2">
                        <tag-collection filter="explicit-tag-match">
                            <condensed-tags>test</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'test'}
            )
        )
        
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags1">
                        <tag-collection filter="implicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                        </tag-collection>
                    </named-field>
                    
                    <named-field name="tags2">
                        <tag-collection filter="explicit-tag-match">
                            <condensed-tags>test</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                tagName='test',
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.valid()
        )
        
        self.assertEqual(
            validateFilter(
                filterElement=ET.fromstring(
                """
                <dict filter="all">
                    <named-field name="tags1">
                        <tag-collection filter="implicit-tag-match">
                            <condensed-tags>int_tag</condensed-tags>
                            <condensed-tags>test</condensed-tags>
                        </tag-collection>
                    </named-field>
                    
                    <named-field name="tags2">
                        <tag-collection filter="explicit-tag-match">
                            <condensed-tags>test</condensed-tags>
                        </tag-collection>
                    </named-field>
                </dict>
                """),
                tagName='test',
                loadedTags=self.tag_collection
            ),
            FilterValidationResult.invalid(
                invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'test'}
            )
        )


if __name__ == '__main__':
    unittest.main()
