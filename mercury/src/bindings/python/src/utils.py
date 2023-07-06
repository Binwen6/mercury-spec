import xml.etree.ElementTree as ET

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'spec-language-interfaces'))

from python_interface.interface import TagNames, AttributeNames


# TODO: write tests
def dictElementToDict(dictElement: ET.Element):
    assert dictElement.tag == TagNames.dictType.value
    
    return {item.attrib[AttributeNames.nameAttribute.value]: item[0] for item in dictElement}