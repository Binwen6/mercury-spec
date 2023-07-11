# code in this file are authored by ChatGPT and finetuned by Trent Fellbootman
import unittest
from lxml import etree as ET
from enum import Enum

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mercury.manifest_validation import (
    checkSyntax, checkTypeDeclarationSyntax, SyntaxValidationResult, ManifestSyntaxInvalidityType
)


# convenient classes
_InvalidityInfo = SyntaxValidationResult.InvalidityInfo
_InvalidityTypes = ManifestSyntaxInvalidityType
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
            invalidityType=_InvalidityTypes.BOOL_ILLEGAL_CHILD,
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
            invalidityType=_InvalidityTypes.BOOL_ILLEGAL_CHILD,
            invalidityPosition=_InvalidityPosition(1)
        )

        self.assertNotEqual(a, b)
        
        a = SyntaxValidationResult.valid()

        b = SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(1)
        )

        self.assertNotEqual(a, b)


class TestCheckSyntax(unittest.TestCase):
    def test_checkSyntax_validDict(self):
        xml_data = """
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
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkSyntax_invalidDict_invalidTag(self):
        xml_data = """
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
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.DICT_INVALID_CHILD_TAG,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkSyntax_invalidDict_duplicateNames(self):
        xml_data = """
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
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.DICT_DUPLICATE_KEYS,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkSyntax_validList(self):
        xml_data = """
                    <list>
                        <string>value1</string>
                        <string>value2</string>
                    </list>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkSyntax_invalidList_invalidChild(self):
        xml_data = """
                    <list>
                        <string>value1</string>
                        <invalid-child>Invalid</invalid-child>
                    </list>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(4)
        ))

    def test_checkSyntax_validNamedField(self):
        xml_data = """
                    <named-field name="field1">
                        <string>value1</string>
                    </named-field>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkSyntax_invalidNamedField_missingName(self):
        xml_data = """
                    <named-field>
                        <string>value1</string>
                    </named-field>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.NAMED_FIELD_MISSING_NAME_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkSyntax_invalidNamedField_invalidChildrenCount(self):
        xml_data = """
                    <named-field name="field1">
                        <string>value1</string>
                        <string>value2</string>
                    </named-field>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.NAMED_FIELD_INCORRECT_CHILDREN_COUNT,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkSyntax_validString(self):
        xml_data = """
                    <string>value1</string>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkSyntax_invalidString_invalidChild(self):
        xml_data = """
                    <string>
                        <invalid-child>Invalid</invalid-child>
                    </string>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.STRING_ILLEGAL_CHILD,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkSyntax_validTypeIdentifier(self):
        xml_data = """
                    <type-declaration>
                        <type-string></type-string>
                    </type-declaration>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkSyntax_invalidTypeIdentifier_invalidChildrenCount(self):
        xml_data = """
                    <type-declaration></type-declaration>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_INCORRECT_CHILD_COUNT,
            invalidityPosition=_InvalidityPosition(2)
        ))


class TestCheckTypeDeclarationSyntax(unittest.TestCase):
    def test_checkTypeDeclarationSyntax_validString(self):
        xml_data = """
                    <type-string></type-string>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkTypeDeclarationSyntax_invalidString_invalidChild(self):
        xml_data = """
                    <type-string>
                        <invalid-child>Invalid</invalid-child>
                    </type-string>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_STRING_ILLEGAL_CONTENT,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkTypeDeclarationSyntax_validTensor(self):
        xml_data = """
                    <type-tensor>
                        <dim>3</dim>
                        <dim>4</dim>
                    </type-tensor>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkTypeDeclarationSyntax_invalidTensor_invalidChild(self):
        xml_data = """
                    <type-tensor>
                        <invalid-child>Invalid</invalid-child>
                    </type-tensor>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_TENSOR_INVALID_CHILD_TAG,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkTypeDeclarationSyntax_validList(self):
        xml_data = """
                    <type-list>
                        <type-string></type-string>
                    </type-list>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkTypeDeclarationSyntax_invalidList_invalidChildrenCount_NotEnough(self):
        xml_data = """
                    <type-list></type-list>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_LIST_INCORRECT_CHILD_COUNT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_checkTypeDeclarationSyntax_invalidList_invalidChildrenCount_TooMany(self):
        xml_data = """
                    <type-list><type-string/><type-string/></type-list>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_LIST_INCORRECT_CHILD_COUNT,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkTypeDeclarationSyntax_validTuple(self):
        xml_data = """
                    <type-tuple>
                        <type-string></type-string>
                        <type-tensor>
                            <dim>3</dim>
                        </type-tensor>
                    </type-tuple>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkTypeDeclarationSyntax_invalidTuple_invalidChild(self):
        xml_data = """
                    <type-tuple>
                        <type-string></type-string>
                        <invalid-child>Invalid</invalid-child>
                    </type-tuple>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(4)
        ))

    def test_checkTypeDeclarationSyntax_validNamedValueCollection(self):
        xml_data = """
                    <type-named-value-collection>
                        <type-named-value name="field1"><type-string/></type-named-value>
                        <type-named-value name="field2"><type-string/></type-named-value>
                    </type-named-value-collection>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkTypeDeclarationSyntax_invalidNamedValueCollection_invalidTag(self):
        xml_data = """
                    <type-named-value-collection>
                        <type-named-value name="field1"><type-string/></type-named-value>
                        <type-named-value name="field2"><type-string/></type-named-value>
                        <invalid-tag>Invalid</invalid-tag>
                    </type-named-value-collection>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_INVALID_CHILD_TAG,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkTypeDeclarationSyntax_invalidNamedValueCollection_duplicateNames(self):
        xml_data = """
                    <type-named-value-collection>
                        <type-named-value name="field1"><type-string/></type-named-value>
                        <type-named-value name="field1"><type-string/></type-named-value>
                    </type-named-value-collection>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkTypeDeclarationSyntax_validNamedValue(self):
        xml_data = """
                    <type-named-value name="field1"><type-string/></type-named-value>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkTypeDeclarationSyntax_invalidNamedValue_missingName(self):
        xml_data = """
                    <type-named-value><type-string/></type-named-value>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_MISSING_NAME_ATTRIBUTE,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkTypeDeclarationSyntax_invalidNamedValue_invalidContent(self):
        xml_data = """
                    <type-named-value name="field1">
                        <invalid-child>Invalid</invalid-child>
                    </type-named-value>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(3)
        ))
    
    def test_checkTypeDeclarationSyntax_invalidNamedValue_NotEnoughChildren(self):
        xml_data = """
                    <type-named-value name="field1">
                    </type-named-value>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_INCORRECT_CHILDREN_COUNT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_checkTypeDeclarationSyntax_invalidNamedValue_TooManyChildren(self):
        xml_data = """
                    <type-named-value name="field1">
                        <type-string/>
                        <type-string/>
                    </type-named-value>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_INCORRECT_CHILDREN_COUNT,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkTypeDeclarationSyntax_validDim(self):
        xml_data = """
                    <dim>3</dim>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkTypeDeclarationSyntax_invalidDim_invalidContent(self):
        xml_data = """
                    <dim>Invalid</dim>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkTypeDeclarationSyntax_invalidTag(self):
        xml_data = """
                    <invalid-tag>Invalid</invalid-tag>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INVALID_TAG,
            invalidityPosition=_InvalidityPosition(2)
        ))


if __name__ == '__main__':
    unittest.main()