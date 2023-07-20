from lxml import etree as ET

import sys
import os

from .specification.interface import TagNames, AttributeNames


# TODO: write tests
def dictElementToDict(dictElement: ET._Element):
    assert dictElement.tag == TagNames.DICT
    
    return {item.attrib[AttributeNames.nameAttribute]: item[0] for item in dictElement}