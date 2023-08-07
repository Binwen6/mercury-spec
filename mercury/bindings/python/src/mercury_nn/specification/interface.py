from lxml import etree as ET
from pathlib import Path
from typing import Sequence, List, Set, Iterable
from dataclasses import dataclass

from ..tag_matching import parseCondensedTags


# TODO: avoid duplication with definition in utils.py
def dictElementToDict(dictElement: ET._Element):
    assert dictElement.tag == TagNames.DICT
    
    return {item.attrib[AttributeNames.nameAttribute]: item[0] for item in dictElement}


class FileNames:
    manifestFile = Path('manifest.xml')


class KeyNames:
    pythonImplementationIdentifier = 'Python'
    specs = 'specs'
    implementations = 'implementations'
    implementationEntryFile = 'entryFile'
    implementationEntryClass = 'entryClass'
    headerKeyName = 'header'
    modelNameKeyName = 'name'
    callSpecsKeyName = 'callSpecs'
    tagsKeyName = 'tags'


class TagNames:
    DICT = 'dict'
    LIST = 'list'
    NAMED_FIELD = 'named-field'
    STRING = 'string'
    BOOL = 'bool'
    INT = 'int'
    FLOAT = 'float'
    TYPE_DECLARATION = 'type-declaration'
    LOGICAL = 'logical'
    TAG_COLLECTION = 'tag-collection'
    CONDENSED_TAGS = 'condensed-tags'


class AttributeNames:
    filterOperationTypeAttribute = 'filter'
    nameAttribute = 'name'


class FilterOperationTypes:
    NONE = 'none'
    ALL = 'all'
    EQUALS = 'equals'

    TYPE_MATCH = 'type-match'
    
    LESS_THAN = 'lt'
    LESS_THAN_OR_EQUALS = 'le'
    GREATER_THAN = 'gt'
    GREATER_THAN_OR_EQUALS = 'ge'
    
    # logical operations
    AND = 'and'
    OR = 'or'
    NOT = 'not'
    
    # tag operations
    IMPLICIT_TAG_MATCH = 'implicit-tag-match'
    EXPLICIT_TAG_MATCH = 'explicit-tag-match'

class TypeDeclarationFilterOperationTypes:
    NONE = 'none'
    ALL = 'all'
    EQUALS = 'equals'
    
    LESS_THAN = 'lt'
    LESS_THAN_OR_EQUALS = 'le'
    GREATER_THAN = 'gt'
    GREATER_THAN_OR_EQUALS = 'ge'


@dataclass
class ImplementationInfo:
    sourceFile: Path
    modelClassName: str


class ManifestUtils:
    
    # TODO: write tests
    @staticmethod
    def _getModelSpecs(manifest: ET._Element) -> ET._Element:
        """Returns the model specs element of the model's manifest data.

        Args:
            manifest (ET._Element): The model's manifest data.

        Returns:
            ET._Element: The model specs element.
        """
        
        return dictElementToDict(manifest)[KeyNames.specs]
    
    # TODO: write tests
    @staticmethod
    def supportPythonImplementation(manifest: ET._Element) -> bool:
        """Returns True if manifest data indicates that model has a Python implementation, False otherwise.

        Args:
            manifest (ET._Element): The model's manifest data.

        Returns:
            bool: Whether the model has a Python implementation.
        """
        
        supported_implementations = set(
            dictElementToDict(dictElementToDict(manifest)[KeyNames.implementations]).keys())

        return KeyNames.pythonImplementationIdentifier in supported_implementations
    
    # TODO: write tests
    @staticmethod
    def getImplementationInfo(manifest: ET._Element):
        implementationDict = dictElementToDict(
            dictElementToDict(dictElementToDict(manifest)[KeyNames.implementations])
            [KeyNames.pythonImplementationIdentifier])
        
        return ImplementationInfo(
            sourceFile=Path(implementationDict[KeyNames.implementationEntryFile].text),
            modelClassName=implementationDict[KeyNames.implementationEntryClass].text
        )
    
    # TODO: write tests
    @staticmethod
    def getModelName(manifest: ET._Element):
        return dictElementToDict(
            dictElementToDict(ManifestUtils._getModelSpecs(manifest))
            [KeyNames.headerKeyName])[KeyNames.modelNameKeyName].text
    
    @staticmethod
    def getCondensedTags(manifest: ET._Element) -> Set[str]:
        tags_element = dictElementToDict(ManifestUtils._getModelSpecs(manifest))[KeyNames.tagsKeyName]
        
        return {element.text for element in tags_element}
    
    @staticmethod
    def getTags(manifest: ET._Element) -> Set[str]:
        condensed_tags = ManifestUtils.getCondensedTags(manifest)
        tag_sets = [parseCondensedTags(item) for item in condensed_tags]

        tags = set()
        for tag_set in tag_sets:
            tags.update(tag_set)
        
        return tags


def filterXMLfromArgs(callSchemes: Iterable[str] | None=None) -> str:
    """Generates XML-format filter description from simple arguments.

    Args:
        callSchemes (Iterable[str] | None): The supported call schemes. E.g., {chat-completion, image-classification}, etc.

    Returns:
        str: The XML representation of the filter requirements.
    """

    return \
f"""
<dict filter="all">
    <named-field name="specs">
        <dict filter="all">
            <named-field name="header">
                <dict filter="all">
                    <named-field name="name">
                        <string filter="none"/>
                    </named-field>
                    <named-field name="description">
                        <string filter="none"/>
                    </named-field>
                </dict>
            </named-field>
            <named-field name="callSpecs">
                <dict filter="all">
                    <named-field name="input">
                        <dict filter="all">
                            <named-field name="type">
                                <type-declaration filter="none"/>
                            </named-field>
                            <named-field name="description">
                                <string filter="none"/>
                            </named-field>
                        </dict>
                    </named-field>
                    <named-field name="output">
                        <dict filter="all">
                            <named-field name="type">
                                <type-declaration filter="none"/>
                            </named-field>
                            <named-field name="description">
                                <string filter="none"/>
                            </named-field>
                        </dict>
                    </named-field>
                </dict>
            </named-field>
            <named-field name="tags">
                {f'''<tag-collection filter="explicit-tag-match">
                    <condensed-tags>
                        {f"call-scheme::{{{', '.join(callSchemes)}}}"}
                    </condensed-tags>
                </tag-collection>''' if callSchemes is not None and len(callSchemes) > 0
                
                else '<tag-collection filter="none"/>'}
            </named-field>
            <named-field name="properties">
                <dict filter="all">
                    <named-field name="benchmarks">
                        <dict filter="none"/>
                    </named-field>
                </dict>
            </named-field>
        </dict>
    </named-field>
    <named-field name="implementations">
        <dict filter="none"/>
    </named-field>
</dict>
"""


class TypeDeclarationTagNames:
    # primitives
    STRING = 'type-string'
    BOOL = 'type-bool'
    INT = 'type-int'
    FLOAT = 'type-float'
    TENSOR = 'type-tensor'

    # composers
    LIST = 'type-list'
    TUPLE = 'type-tuple'

    # others
    NAMED_VALUE_COLLECTION = 'type-named-value-collection'
    NAMED_VALUE = 'type-named-value'

    # auxiliary tag names
    DIM = 'dim'


class TypeDeclarationAttributeNames:
    namedValueNameAttributeName = 'name'


class FilterSyntaxInvalidityType:
    INVALID_TAG = 'INVALID_TAG'
    INVALID_FILTER_OPERATION_TYPE = 'INVALID_FILTER_OPERATION_TYPE'
    MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE = 'MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE'
    ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE = 'ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE'
    
    DICT_INVALID_CHILD_TAG = 'DICT_INVALID_CHILD_TAG'
    DICT_DUPLICATE_KEYS = 'DICT_DUPLICATE_KEYS'
    
    LOGICAL_INCORRECT_CHILD_COUNT = 'LOGICAL_INCORRECT_CHILD_COUNT'
    
    NAMED_FIELD_MISSING_NAME_ATTRIBUTE = 'NAMED_FIELD_MISSING_NAME_ATTRIBUTE'
    NAMED_FIELD_INCORRECT_CHILDREN_COUNT = 'NAMED_FIELD_INCORRECT_CHILDREN_COUNT'
    
    ILLEGAL_CHILD_ON_TERMINAL_ELEMENT = 'ILLEGAL_CHILD_ON_TERMINAL_ELEMENT'
    
    INT_INVALID_INT_LITERAL = 'INT_INVALID_INT_LITERAL'
    FLOAT_INVALID_FLOAT_LITERAL = 'FLOAT_INVALID_FLOAT_LITERAL'
    BOOL_INVALID_BOOL_LITERAL = 'BOOL_INVALID_BOOL_LITERAL'
    
    TYPE_DECLARATION_INCORRECT_CHILD_COUNT = 'TYPE_DECLARATION_INCORRECT_CHILD_COUNT'
    
    TYPE_DECLARATION_TENSOR_INVALID_CHILD_TAG = 'TYPE_DECLARATION_TENSOR_INVALID_CHILD_TAG'
    
    TYPE_DECLARATION_DIM_ILLEGAL_CHILD = 'TYPE_DECLARATION_DIM_ILLEGAL_CHILD'
    TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL = 'TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL'
    
    TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT = 'TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT'
    
    TYPE_DECLARATION_LIST_INCORRECT_CHILD_COUNT = 'TYPE_DECLARATION_LIST_INCORRECT_CHILD_COUNT'
    
    TYPE_DECLARATION_NAMED_VALUE_COLLECTION_INVALID_CHILD_TAG = 'TYPE_DECLARATION_NAMED_VALUE_COLLECTION_INVALID_CHILD_TAG'
    TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS = 'TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS'
    
    TYPE_DECLARATION_NAMED_VALUE_MISSING_NAME_ATTRIBUTE = 'TYPE_DECLARATION_NAMED_VALUE_MISSING_NAME_ATTRIBUTE'
    TYPE_DECLARATION_NAMED_VALUE_INCORRECT_CHILDREN_COUNT = 'TYPE_DECLARATION_NAMED_VALUE_INCORRECT_CHILDREN_COUNT'

    TAG_COLLECTION_INVALID_CHILD_TAG = 'TAG_COLLECTION_INVALID_CHILD_TAG'
    CONDENSED_TAGS_ILLEGAL_FILTER_OPERATION_ATTRIBUTE = 'CONDENSED_TAGS_ILLEGAL_FILTER_OPERATION_ATTRIBUTE'
    CONDENSED_TAGS_ILLEGAL_EMPTY_CONTENT = 'CONDENSED_TAGS_ILLEGAL_EMPTY_CONTENT'
    CONDENSED_TAGS_ILLEGAL_CHILD = 'CONDENSED_TAGS_ILLEGAL_CHILD'
    CONDENSED_TAGS_INVALID_SYNTAX = 'CONDENSED_TAGS_INVALID_SYNTAX'


class ManifestSyntaxInvalidityType:
    INVALID_TAG = 'INVALID_TAG'

    DICT_INVALID_CHILD_TAG = 'DICT_INVALID_CHILD_TAG'
    DICT_DUPLICATE_KEYS = 'DICT_DUPLICATE_KEYS'
    
    NAMED_FIELD_MISSING_NAME_ATTRIBUTE = 'NAMED_FIELD_MISSING_NAME_ATTRIBUTE'
    NAMED_FIELD_INCORRECT_CHILDREN_COUNT = 'NAMED_FIELD_INCORRECT_CHILDREN_COUNT'
    
    # a terminal element cannot have any children
    ILLEGAL_CHILD_ON_TERMINAL_ELEMENT = 'ILLEGAL_CHILD_ON_TERMINAL_ELEMENT'

    INT_INVALID_INT_LITERAL = 'INT_INVALID_INT_LITERAL'
    FLOAT_INVALID_FLOAT_LITERAL = 'FLOAT_INVALID_FLOAT_LITERAL'
    BOOL_INVALID_BOOL_LITERAL = 'BOOL_INVALID_BOOL_LITERAL'
    
    TYPE_DECLARATION_INCORRECT_CHILD_COUNT = 'TYPE_DECLARATION_INCORRECT_CHILD_COUNT'
    
    TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT = 'TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT'
    
    TYPE_DECLARATION_TENSOR_INVALID_CHILD_TAG = 'TYPE_DECLARATION_TENSOR_INVALID_CHILD_TAG'

    TYPE_DECLARATION_LIST_INCORRECT_CHILD_COUNT = 'TYPE_DECLARATION_LIST_INCORRECT_CHILD_COUNT'

    TYPE_DECLARATION_NAMED_VALUE_COLLECTION_INVALID_CHILD_TAG = 'TYPE_DECLARATION_NAMED_VALUE_COLLECTION_INVALID_CHILD_TAG'
    TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS = 'TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS'
    
    TYPE_DECLARATION_NAMED_VALUE_MISSING_NAME_ATTRIBUTE = 'TYPE_DECLARATION_NAMED_VALUE_MISSING_NAME_ATTRIBUTE'
    TYPE_DECLARATION_NAMED_VALUE_INCORRECT_CHILDREN_COUNT = 'TYPE_DECLARATION_NAMED_VALUE_INCORRECT_CHILDREN_COUNT'
    
    TYPE_DECLARATION_DIM_ILLEGAL_CHILD = 'TYPE_DECLARATION_DIM_ILLEGAL_CHILD'
    TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL = 'TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL'

    TAG_COLLECTION_INVALID_CHILD_TAG = 'TAG_COLLECTION_INVALID_CHILD_TAG'
    CONDENSED_TAGS_ILLEGAL_CHILD = 'CONDENSED_TAGS_ILLEGAL_CHILD'
    CONDENSED_TAGS_ILLEGAL_EMPTY_CONTENT = 'CONDENSED_TAGS_ILLEGAL_EMPTY_CONTENT'
    CONDENSED_TAGS_INVALID_SYNTAX = 'CONDENSED_TAGS_INVALID_SYNTAX'

class FilterMatchFailureType:
    TAG_MISMATCH = 'TAG_MISMATCH'
    # TODO: add more types
    
    DICT_MISSING_KEY = 'DICT_MISSING_KEY'
    
    LIST_INSUFFICIENT_CHILDREN = 'LIST_INSUFFICIENT_CHILDREN'
    
    STRING_VALUE_NOT_EQUAL = 'STRING_VALUE_NOT_EQUAL'

    BOOL_VALUE_NOT_EQUAL = 'BOOL_VALUE_NOT_EQUAL'

    NUMERIC_FAILED_COMPARISON = 'NUMERIC_FAILED_COMPARISON'
    
    TYPE_DECLARATION_TUPLE_INCORRECT_CHILDREN_COUNT = 'TYPE_DECLARATION_TUPLE_INCORRECT_CHILDREN_COUNT'

    TYPE_DECLARATION_TENSOR_DIFFERENT_DIM_NUMBER = 'TYPE_DECLARATION_TENSOR_DIFFERENT_DIM_NUMBER'
    
    TYPE_DECLARATION_DIM_FAILED_COMPARISON = 'TYPE_DECLARATION_DIM_FAILED_COMPARISON'
    
    TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DIFFERENT_KEYS = 'TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DIFFERENT_KEYS'

    LOGICAL_OPERATION_MATCH_FAILURE = 'LOGICAL_OPERATION_MATCH_FAILURE'

    TAG_COLLECTION_EXPLICIT_TAG_MATCH_FAILURE = 'TAG_COLLECTION_EXPLICIT_TAG_MATCH_FAILURE'
    