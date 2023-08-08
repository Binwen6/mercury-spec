# code in this file are authored by ChatGPT and finetuned by Trent Fellbootman
import unittest
from lxml import etree as ET
from enum import Enum

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().resolve().parent.parent.parent))

from src.mercury_nn.validation.manifest_validation import (
    checkSyntax, checkTypeDeclarationSyntax, SyntaxValidationResult, ManifestSyntaxInvalidityType,
    ManifestValidationResult, validateManifest
)

from src.mercury_nn.filtering import Filter, FilterMatchResult
from src.mercury_nn.specification.interface import FilterMatchFailureType


# convenient classes
_InvalidityInfo = SyntaxValidationResult.InvalidityInfo
_InvalidityTypes = ManifestSyntaxInvalidityType
_InvalidityPosition = SyntaxValidationResult.InvalidityInfo.InvalidityPosition


# override ManifestUtil methods for toy data
from src.mercury_nn.utils import dictElementToDict
from src.mercury_nn.tag_matching import parseCondensedTags
from src.mercury_nn.specification.interface import ManifestUtils


def _getTags(manifest: ET._Element):
    tag_sets = [parseCondensedTags(child.text) for child in dictElementToDict(manifest)['tags']]
    tags = set()

    for tag_set in tag_sets:
        tags.update(tag_set)

    return tags

ManifestUtils.getTags = _getTags


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
            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
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
            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
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

    def test_checkSyntax_validDict_noKeys(self):
        xml_data = """
                    <dict></dict>"""
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
            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_checkSyntax_validBool(self):
        xml_data = """
                    <bool>true</bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
        
        xml_data = """
                    <bool>True</bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
        
        xml_data = """
                    <bool>TRUE</bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
        
        xml_data = """
                    <bool>1</bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
        
        xml_data = """
                    <bool>false</bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
        
        xml_data = """
                    <bool>False</bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
        
        xml_data = """
                    <bool>FALSE</bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
        
        xml_data = """
                    <bool>0</bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
        
        xml_data = """
                    <bool>unfilled</bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_checkSyntax_invalidBool_invalidLiteral(self):
        xml_data = """
                    <bool>invalid</bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.BOOL_INVALID_BOOL_LITERAL,
            invalidityPosition=_InvalidityPosition(2)
        ))

    def test_checkSyntax_invalidBool_invalidChild(self):
        xml_data = """
                    <bool>
                        <invalid-child>Invalid</invalid-child>
                    </bool>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_checkSyntax_validInt(self):
        xml_data = """
                    <int>1</int>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkSyntax_invalidInt_invalidChild(self):
        xml_data = """
                    <int>
                        <invalid-child>Invalid</invalid-child>
                    </int>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_checkSyntax_invalidInt_invalidIntLiteral(self):
        xml_data = """
                    <int>1.0</int>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.INT_INVALID_INT_LITERAL,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_checkSyntax_validFloat(self):
        xml_data = """
                    <float>1</float>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
        
        xml_data = """
                    <float>1.0</float>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkSyntax_invalidFloat_invalidChild(self):
        xml_data = """
                    <float>
                        <invalid-child>Invalid</invalid-child>
                    </float>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_checkSyntax_invalidFloat_invalidFloatLiteral(self):
        xml_data = """
                    <float>test</float>"""
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.FLOAT_INVALID_FLOAT_LITERAL,
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

    # Test type declarations
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
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_checkTypeDeclarationSyntax_validBool(self):
        xml_data = """
                    <type-bool></type-bool>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkTypeDeclarationSyntax_invalidBool_illegalContent(self):
        xml_data = """
                    <type-bool>test</type-bool>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_checkTypeDeclarationSyntax_validInt(self):
        xml_data = """
                    <type-int></type-int>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkTypeDeclarationSyntax_invalidInt_illegalContent(self):
        xml_data = """
                    <type-int>test</type-int>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_checkTypeDeclarationSyntax_validFloat(self):
        xml_data = """
                    <type-float></type-float>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

    def test_checkTypeDeclarationSyntax_invalidFloat_illegalContent(self):
        xml_data = """
                    <type-float>test</type-float>"""
        element = ET.fromstring(xml_data)
        result = checkTypeDeclarationSyntax(element)
        self.assertTrue(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
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
    
    def test_checkTypeDeclarationSyntax_validNamedValueCollection_noKeys(self):
        xml_data = """
                    <type-named-value-collection></type-named-value-collection>"""
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
    
    # Test tags
    def test_TagCollection_ValidNonEmpty(self):
        xml_data = """
        <tag-collection>
            <condensed-tags>test</condensed-tags>
        </tag-collection>
        """

        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_TagCollection_ValidEmpty(self):
        xml_data = """
        <tag-collection/>
        """

        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())

        xml_data = """
        <tag-collection></tag-collection>
        """

        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.valid())
    
    def test_TagCollection_InvalidChildTag(self):
        xml_data = """
        <tag-collection>
            <invalid-tag>int_tag</invalid-tag>
        </tag-collection>
        """

        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.TAG_COLLECTION_INVALID_CHILD_TAG,
            invalidityPosition=_InvalidityPosition(2)
        ))
    
    def test_Tag_IllegalChild(self):
        xml_data = """
        <tag-collection>
            <condensed-tags>int_tag<string>koala</string></condensed-tags>
        </tag-collection>
        """
        
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_CHILD,
            invalidityPosition=_InvalidityPosition(3)
        ))
    
    def test_Tag_IllegalEmptyContent(self):
        xml_data = """
        <tag-collection>
            <condensed-tags></condensed-tags>
        </tag-collection>
        """
        
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_EMPTY_CONTENT,
            invalidityPosition=_InvalidityPosition(3)
        ))
        
        xml_data = """
        <tag-collection>
            <condensed-tags/>
        </tag-collection>
        """
        
        element = ET.fromstring(xml_data)
        result = checkSyntax(element)
        self.assertEqual(result, SyntaxValidationResult.invalid(
            invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_EMPTY_CONTENT,
            invalidityPosition=_InvalidityPosition(3)
        ))


class TestManifestValidationResult(unittest.TestCase):
    
    def test_InvalidityInfo(self):
        self.assertTrue(
            ManifestValidationResult.InvalidityInfo(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                info={'a', 'b'}
            ) ==
            ManifestValidationResult.InvalidityInfo(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                info={'a', 'b'}
            )
        )
        
        self.assertFalse(
            ManifestValidationResult.InvalidityInfo(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                info={'a', 'b'}
            ) ==
            ManifestValidationResult.InvalidityInfo(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                info={'a', 'c'}
            )
        )
        
        self.assertFalse(
            ManifestValidationResult.InvalidityInfo(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                info={'a', 'b'}
            ) ==
            ManifestValidationResult.InvalidityInfo(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                info={'a', 'b'}
            )
        )

    def test_ManifestValidationResult(self):
        self.assertTrue(
            ManifestValidationResult.valid() ==
            ManifestValidationResult.valid()
        )

        self.assertTrue(
            ManifestValidationResult.invalid(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a', 'b'}
            ) ==
            ManifestValidationResult.invalid(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a', 'b'}
            )
        )
        
        self.assertFalse(
            ManifestValidationResult.valid() ==
            ManifestValidationResult.invalid(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a', 'b'}
            )
        )
        
        self.assertFalse(
            ManifestValidationResult.invalid(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a', 'b'}
            ) ==
            ManifestValidationResult.invalid(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a', 'c'}
            )
        )
        
        self.assertTrue(ManifestValidationResult.valid().isValid)
        self.assertFalse(ManifestValidationResult.invalid(
                invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                invalidityInfo={'a', 'b'}
            ).isValid)


class TestValidateManifest(unittest.TestCase):
    
    def test_Valid_Tags(self):
        manifest = ET.fromstring("""
        <dict>
            <named-field name="data">
                <int>4</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection>
                    <condensed-tags>gt1.gt2.gt3</condensed-tags>
                    <condensed-tags>explicit</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """)
        
        self.assertEqual(validateManifest(manifest, self.base_model_filter, self.tag_collection), ManifestValidationResult.valid())
    
    def test_Invalid_syntax(self):
        manifest = ET.fromstring("""
        <tag-collection>
            <named-field><string/></named-field>
        </tag-collection>
        """)

        self.assertEqual(validateManifest(manifest, self.base_model_filter, self.tag_collection),
                         ManifestValidationResult.invalid(
                             invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
                             invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                                 invalidityType=ManifestSyntaxInvalidityType.TAG_COLLECTION_INVALID_CHILD_TAG,
                                 invalidityPosition=SyntaxValidationResult.InvalidityInfo.InvalidityPosition(2)
                             )
                         ))
    
    def test_Invalid_UnfilledValue(self):
        manifest = ET.fromstring("""
        <dict>
            <named-field name="tags">
                <tag-collection/>
            </named-field>

            <named-field name="data">
                <int>unfilled</int>
            </named-field>
        </dict>
        """)
        
        self.assertEqual(validateManifest(manifest, self.base_model_filter, self.tag_collection),
                         ManifestValidationResult.invalid(
                             invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNFILLED_VALUE,
                             invalidityInfo=8
                         ))
        
        manifest = ET.fromstring("""
        <dict>
            <named-field name="tags">
                <tag-collection/>
            </named-field>

            <named-field name="data">
                <int>0</int>
            </named-field>
            
            <named-field name="dict">
                <dict>
                    <named-field name="data">
                        <float>unfilled</float>
                    </named-field>
                </dict>
            </named-field>
        </dict>
        """)
        
        self.assertEqual(validateManifest(manifest, self.base_model_filter, self.tag_collection),
                         ManifestValidationResult.invalid(
                             invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNFILLED_VALUE,
                             invalidityInfo=14
                         ))
        
        manifest = ET.fromstring("""
        <dict>
            <named-field name="tags">
                <tag-collection/>
            </named-field>

            <named-field name="data">
                <int>0</int>
            </named-field>
            
            <named-field name="dict">
                <dict>
                    <named-field name="data">
                        <float>0</float>
                    </named-field>
                    
                    <named-field name="dict">
                        <dict>
                            <named-field name="data">
                                <bool>unfilled</bool>
                            </named-field>
                        </dict>
                    </named-field>
                </dict>
            </named-field>
        </dict>
        """)
        
        self.assertEqual(validateManifest(manifest, self.base_model_filter, self.tag_collection),
                         ManifestValidationResult.invalid(
                             invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNFILLED_VALUE,
                             invalidityInfo=20
                         ))
    
    def test_Invalid_BaseModelFilterMismatch(self):
        manifest = ET.fromstring("""
        <string/>
        """)

        self.assertEqual(validateManifest(manifest, self.base_model_filter, self.tag_collection),
                         ManifestValidationResult.invalid(
                             invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.FAILED_BASE_MODEL_FILTER_MATCH,
                             invalidityInfo=FilterMatchResult.FailureInfo(
                                 failureType=FilterMatchFailureType.TAG_MISMATCH,
                                 failurePosition=FilterMatchResult.FailureInfo.FailurePosition(2, 2, [])
                             )
                         ))
    
    def test_Invalid_UnknownTags(self):
        manifest = ET.fromstring("""
        <dict>
            <named-field name="data">
                <int>1</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection>
                    <condensed-tags>test.test</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """)

        self.assertEqual(validateManifest(manifest, self.base_model_filter, self.tag_collection),
                         ManifestValidationResult.invalid(
                             invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
                             invalidityInfo={'test', 'test::test'}
                         ))
    
    def test_invalid_TagMatchFailure(self):
        manifest = ET.fromstring("""
        <dict>
            <named-field name="data">
                <int>3</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection>
                    <condensed-tags>gt1.gt2</condensed-tags>
                    <condensed-tags>gt1.gt2.gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """)
        
        self.assertEqual(validateManifest(manifest, self.base_model_filter, self.tag_collection), ManifestValidationResult.invalid(
            invalidityType=ManifestValidationResult.InvalidityInfo.InvalidityType.UNMATCHED_TAG,
            invalidityInfo=('gt1::gt2::gt3', FilterMatchResult.FailureInfo(
                failureType=FilterMatchFailureType.NUMERIC_FAILED_COMPARISON,
                failurePosition=FilterMatchResult.FailureInfo.FailurePosition(4, 4, [])
            ))
        ))
    
    def setUp(self):
        base_model_filter = ET.fromstring("""
        <dict filter="all">
            <named-field name="data">
                <int filter="none"/>
            </named-field>
            
            <named-field name="tags">
                <tag-collection filter="none"/>
            </named-field>
        </dict>
        """)
        
        tag_gt1 = ET.fromstring("""
        <dict filter="all">
            <named-field name="data">
                <int filter="gt">1</int>
            </named-field>
        </dict>
        """)

        tag_gt1_gt2 = ET.fromstring("""
        <dict filter="all">
            <named-field name="data">
                <int filter="gt">2</int>
            </named-field>
        </dict>
        """)

        tag_gt1_gt2_gt3 = ET.fromstring("""
        <dict filter="all">
            <named-field name="data">
                <int filter="gt">3</int>
            </named-field>
        </dict>
        """)
        
        tag_explicit = ET.fromstring("""
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="explicit-tag-match">
                    <condensed-tags>explicit</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """)
        
        self.base_model_filter = Filter.fromXMLElement(base_model_filter)

        self.tag_collection = {
            'gt1': tag_gt1,
            'gt1::gt2': tag_gt1_gt2,
            'gt1::gt2::gt3': tag_gt1_gt2_gt3,
            'explicit': tag_explicit
        }


if __name__ == '__main__':
    unittest.main()