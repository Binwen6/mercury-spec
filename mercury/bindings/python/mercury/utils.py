from lxml import etree as ET

import sys
import os

from .interface import TagNames, AttributeNames


# TODO: write tests
def dictElementToDict(dictElement: ET._Element):
    assert dictElement.tag == TagNames.DICT.value
    
    return {item.attrib[AttributeNames.nameAttribute.value]: item[0] for item in dictElement}