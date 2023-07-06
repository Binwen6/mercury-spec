from enum import Enum
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Sequence
from dataclasses import dataclass


# TODO: avoid duplication with definition in utils.py
def dictElementToDict(dictElement: ET.Element):
    assert dictElement.tag == TagNames.dictType.value
    
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
    dictType = 'dict'
    listType = 'list'
    namedField = 'named-field'
    string = 'string'
    typeIdentifier = 'type-declaration'
    time = 'time'


class AttributeNames(Enum):
    filterOperationTypeAttribute = 'filter'
    nameAttribute = 'name'


class FilterOperationTypes(Enum):
    none = 'none'
    all = 'all'
    equals = 'equals'


@dataclass
class ImplementationInfo:
    sourceFile: Path
    modelClassName: str


# TODO: write tests
class MetadataUtils:
    
    @staticmethod
    def getModelSpecs(metadata: ET.Element) -> ET.Element:
        """Returns the metadata element of the model's manifest data.

        Args:
            metadata (ET.Element): The model's manifest data.

        Returns:
            ET.Element: The metadata element.
        """
        
        return dictElementToDict(metadata)[KeyNames.specs.value]
    
    @staticmethod
    def supportPythonImplementation(metadata: ET.Element) -> bool:
        """Returns True if manifest data indicates that model has a Python implementation, False otherwise.

        Args:
            metadata (ET.Element): The model's manifest data.

        Returns:
            bool: Whether the model has a Python implementation.
        """
        
        supported_implementations = set(
            dictElementToDict(dictElementToDict(metadata)[KeyNames.implementations.value]).keys())

        return KeyNames.pythonImplementationIdentifier.value in supported_implementations
    
    @staticmethod
    def getImplementationInfo(metadata: ET.Element):
        implementationDict = dictElementToDict(
            dictElementToDict(dictElementToDict(metadata)[KeyNames.implementations.value])
            [KeyNames.pythonImplementationIdentifier.value])
        
        return ImplementationInfo(
            sourceFile=Path(implementationDict[KeyNames.implementationEntryFile.value].text),
            modelClassName=implementationDict[KeyNames.implementationEntryClass.value].text
        )
    
    @staticmethod
    def getModelName(metadata: ET.Element):
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
f"""<?xml version="1.0" encoding="UTF-8"?>
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
        {'<list filter="none"/>' if capabilities == None or len(capabilities) == 0 else f'<list filter="all">' + ''.join(f'<string filter="equals">{capability}</string>' for capability in capabilities) + '</list>'}
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
    TENSOR = 'type-tensor'

    # composers
    LIST = 'type-list'
    TUPLE = 'type-tuple'

    # others
    NAMED_VALUE_COLLECTION = 'type-named-value-collection'
    NAMED_VALUE = 'type-named-value'
