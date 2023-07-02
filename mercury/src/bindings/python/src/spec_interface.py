from enum import Enum
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass


# TODO: avoid duplication with definition in utils.py
def dictElementToDict(dictElement: ET.Element):
    assert dictElement.tag == TagNames.dictType.value
    
    return {item.attrib[AttributeNames.nameAttribute.value]: item[0] for item in dictElement}


class FileNames(Enum):
    manifestFile = Path('manifest.xml')


class KeyNames(Enum):
    pythonImplementationIdentifier = 'Python'
    modelSpecs = 'modelSpecs'
    implementations = 'implementations'
    implementationEntryFile = 'entryFile'
    implementationEntryClass = 'entryClass'


class TagNames(Enum):
    dictType = 'dict'
    listType = 'list'
    namedField = 'named-field'
    string = 'string'
    typeIdentifier = 'type-identifier'
    time = 'time'


class AttributeNames(Enum):
    filterOperationTypeAttribute = 'filter'
    nameAttribute = 'name'


class FilterOperationTypes(Enum):
    none = 'none'
    all = 'all'


@dataclass
class ImplementationInfo:
    sourceFile: Path
    modelClassName: str


# TODO: write tests
class ManifestUtils:
    
    @staticmethod
    def getMetadata(manifestData: ET.Element) -> ET.Element:
        """Returns the metadata element of the model's manifest data.

        Args:
            manifestData (ET.Element): The model's manifest data.

        Returns:
            ET.Element: The metadata element.
        """
        
        return dictElementToDict(manifestData)[KeyNames.modelSpecs.value]
    
    @staticmethod
    def supportPythonImplementation(manifestData: ET.Element) -> bool:
        """Returns True if manifest data indicates that model has a Python implementation, False otherwise.

        Args:
            manifestData (ET.Element): The model's manifest data.

        Returns:
            bool: Whether the model has a Python implementation.
        """
        
        supported_implementations = set(
            dictElementToDict(dictElementToDict(manifestData)[KeyNames.implementations.value]).keys())

        return KeyNames.pythonImplementationIdentifier.value in supported_implementations
    
    @staticmethod
    def getImplementationInfo(manifestData: ET.Element):
        implementationDict = dictElementToDict(
            dictElementToDict(dictElementToDict(manifestData)[KeyNames.implementations.value])
            [KeyNames.pythonImplementationIdentifier.value])
        
        return ImplementationInfo(
            sourceFile=Path(implementationDict[KeyNames.implementationEntryFile.value][0].text),
            modelClassName=implementationDict[KeyNames.implementationEntryClass.value][0].text
        )
