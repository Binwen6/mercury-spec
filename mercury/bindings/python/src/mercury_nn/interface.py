from enum import Enum
from lxml import etree as ET
from pathlib import Path
from typing import Sequence
from dataclasses import dataclass


# TODO: avoid duplication with definition in utils.py
def dictElementToDict(dictElement: ET._Element):
    assert dictElement.tag == TagNames.DICT.value
    
    return {item.attrib[AttributeNames.nameAttribute.value]: item[0] for item in dictElement}


class FileNames(Enum):
    manifestFile = Path('manifest.xml')


class KeyNames(Enum):
    pythonImplementationIdentifier = 'Python'
    specs = 'specs'
    implementations = 'implementations'
    implementationEntryFile = 'entryFile'
    implementationEntryClass = 'entryClass'
    headerKeyName = 'header'
    modelNameKeyName = 'name'


class TagNames(Enum):
    DICT = 'dict'
    LIST = 'list'
    NAMED_FIELD = 'named-field'
    STRING = 'string'
    BOOL = 'bool'
    INT = 'int'
    FLOAT = 'float'
    TYPE_DECLARATION = 'type-declaration'


class AttributeNames(Enum):
    filterOperationTypeAttribute = 'filter'
    nameAttribute = 'name'


class FilterOperationTypes(Enum):
    NONE = 'none'
    ALL = 'all'
    EQUALS = 'equals'

    TYPE_MATCH = 'type-match'
    
    LESS_THAN = 'lt'
    LESS_THAN_OR_EQUALS = 'le'
    GREATER_THAN = 'gt'
    GREATER_THAN_OR_EQUALS = 'ge'


class TypeDeclarationFilterOperationTypes(Enum):
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


# TODO: write tests
class MetadataUtils:
    
    @staticmethod
    def getModelSpecs(metadata: ET._Element) -> ET._Element:
        """Returns the metadata element of the model's manifest data.

        Args:
            metadata (ET._Element): The model's manifest data.

        Returns:
            ET._Element: The metadata element.
        """
        
        return dictElementToDict(metadata)[KeyNames.specs.value]
    
    @staticmethod
    def supportPythonImplementation(metadata: ET._Element) -> bool:
        """Returns True if manifest data indicates that model has a Python implementation, False otherwise.

        Args:
            metadata (ET._Element): The model's manifest data.

        Returns:
            bool: Whether the model has a Python implementation.
        """
        
        supported_implementations = set(
            dictElementToDict(dictElementToDict(metadata)[KeyNames.implementations.value]).keys())

        return KeyNames.pythonImplementationIdentifier.value in supported_implementations
    
    @staticmethod
    def getImplementationInfo(metadata: ET._Element):
        implementationDict = dictElementToDict(
            dictElementToDict(dictElementToDict(metadata)[KeyNames.implementations.value])
            [KeyNames.pythonImplementationIdentifier.value])
        
        return ImplementationInfo(
            sourceFile=Path(implementationDict[KeyNames.implementationEntryFile.value].text),
            modelClassName=implementationDict[KeyNames.implementationEntryClass.value].text
        )
    
    @staticmethod
    def getModelName(metadata: ET._Element):
        return dictElementToDict(
            dictElementToDict(MetadataUtils.getModelSpecs(metadata))
            [KeyNames.headerKeyName.value])[KeyNames.modelNameKeyName.value].text


def filterXMLfromArgs(modelType: str | None=None, callScheme: str | None=None, capabilities: Sequence[str] | None=None) -> str:
    """Generates XML-format filter description from simple arguments.

    Args:
        modelType (str | None): The type of the model. E.g., chat-completion, image-classification, etc.
        callScheme (str | None): The call scheme. E.g., chat-completion, image-classification, etc.
        capabilities (Sequence[str] | None): The required capabilities. E.g., question-answering, math, etc.

    Returns:
        str: The XML representation of the filter requirements.
    """

    return \
f"""
<dict filter="all">
    <named-field name="header">
        <dict filter="all">
            <named-field name="name">
                <string filter="none"/>
            </named-field>
            <named-field name="class">
                {'<string filter="none"/>' if modelType is None else f'<string filter="equals">{modelType}</string>'}
            </named-field>
            <named-field name="description">
                <string filter="none"/>
            </named-field>
        </dict>
    </named-field>
    <named-field name="capabilities">
        {'<dict filter="none"/>' if capabilities == None or len(capabilities) == 0 else f'<dict filter="all">' + ''.join(f'<named-field name="{capability}"><string filter="none"/></named-field>' for capability in capabilities) + '</dict>'}
    </named-field>
    <named-field name="callSpecs">
        <dict filter="all">
            <named-field name="callScheme">
                {'<string filter="none"/>' if callScheme is None else f'<string filter="equals">{callScheme}</string>'}
            </named-field>
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
    <named-field name="properties">
        <dict filter="none"/>
    </named-field>
</dict>
"""


class TypeDeclarationTagNames(Enum):
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


class TypeDeclarationAttributeNames(Enum):
    namedValueNameAttributeName = 'name'


class FilterSyntaxInvalidityType(Enum):
    INVALID_TAG = 'INVALID_TAG'
    INVALID_FILTER_OPERATION_TYPE = 'INVALID_FILTER_OPERATION_TYPE'
    MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE = 'MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE'
    ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE = 'ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE'
    
    DICT_INVALID_CHILD_TAG = 'DICT_INVALID_CHILD_TAG'
    DICT_DUPLICATE_KEYS = 'DICT_DUPLICATE_KEYS'
    
    NAMED_FIELD_MISSING_NAME_ATTRIBUTE = 'NAMED_FIELD_MISSING_NAME_ATTRIBUTE'
    NAMED_FIELD_INCORRECT_CHILDREN_COUNT = 'NAMED_FIELD_INCORRECT_CHILDREN_COUNT'
    
    ILLEGAL_CHILD_ON_TERMINAL_ELEMENT = 'ILLEGAL_CHILD_ON_TERMINAL_ELEMENT'
    
    INT_INVALID_INT_LITERAL = 'INT_INVALID_INT_LITERAL'
    FLOAT_INVALID_FLOAT_LITERAL = 'FLOAT_INVALID_FLOAT_LITERAL'
    
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


class ManifestSyntaxInvalidityType(Enum):
    INVALID_TAG = 'INVALID_TAG'

    DICT_INVALID_CHILD_TAG = 'DICT_INVALID_CHILD_TAG'
    DICT_DUPLICATE_KEYS = 'DICT_DUPLICATE_KEYS'
    
    NAMED_FIELD_MISSING_NAME_ATTRIBUTE = 'NAMED_FIELD_MISSING_NAME_ATTRIBUTE'
    NAMED_FIELD_INCORRECT_CHILDREN_COUNT = 'NAMED_FIELD_INCORRECT_CHILDREN_COUNT'
    
    # a terminal element cannot have any children
    ILLEGAL_CHILD_ON_TERMINAL_ELEMENT = 'ILLEGAL_CHILD_ON_TERMINAL_ELEMENT'

    INT_INVALID_INT_LITERAL = 'INT_INVALID_INT_LITERAL'
    FLOAT_INVALID_FLOAT_LITERAL = 'FLOAT_INVALID_FLOAT_LITERAL'
    
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

class FilterMatchFailureType(Enum):
    TAG_MISMATCH = 'TAG_MISMATCH'
    # TODO: add more types
    
    DICT_MISSING_KEY = 'DICT_MISSING_KEY'
    
    LIST_INSUFFICIENT_CHILDREN = 'LIST_INSUFFICIENT_CHILDREN'
    
    STRING_VALUE_NOT_EQUAL = 'STRING_VALUE_NOT_EQUAL'

    NUMERIC_FAILED_COMPARISON = 'NUMERIC_FAILED_COMPARISON'
    
    TYPE_DECLARATION_TUPLE_INCORRECT_CHILDREN_COUNT = 'TYPE_DECLARATION_TUPLE_INCORRECT_CHILDREN_COUNT'

    TYPE_DECLARATION_TENSOR_DIFFERENT_DIM_NUMBER = 'TYPE_DECLARATION_TENSOR_DIFFERENT_DIM_NUMBER'
    
    TYPE_DECLARATION_DIM_FAILED_COMPARISON = 'TYPE_DECLARATION_DIM_FAILED_COMPARISON'
    
    TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DIFFERENT_KEYS = 'TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DIFFERENT_KEYS'
