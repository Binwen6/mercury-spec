from ..config import Config
from lxml import etree as ET


def loadBaseModelFilter() -> ET._Element:
    return ET.parse(Config.baseModelFilterPath).getroot()
