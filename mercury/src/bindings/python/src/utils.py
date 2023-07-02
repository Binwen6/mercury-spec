import xml.etree.ElementTree as ET

from .spec_interface import TagNames, AttributeNames


# TODO: write tests
def dictElementToDict(dictElement: ET.Element):
    assert dictElement.tag == TagNames.dictType.value
    
    return {item.attrib[AttributeNames.nameAttribute.value]: item[0] for item in dictElement}