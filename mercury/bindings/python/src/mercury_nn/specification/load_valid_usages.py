from lxml import etree as ET
from dataclasses import dataclass
from typing import Dict
from pathlib import Path

import sys
import os

from ..config import Config


@dataclass
class ValidUsage:
    name: str
    description: str


def loadValidUsage(filepath: Path) -> Dict[str, ValidUsage]:
    
    """Loads valid usage specifications from a file.
    
    The file must be an XML with the following form:
    
    <?xml version="1.0" encoding="UTF-8"?>
    <array>
        <valid-usage>
            <name>...</name>
            <description>
                ...
            </description>
        </valid-usage>
        
        ...
    </array>
    
    Currently, this function does NOT check the validity of the file.

    Returns:
        Dict[str, ValidUsage]: The valid usages.
            The keys are the IDs (currently, the IDs are just the names);
            the values are `ValidUsage` objects.
    """
    
    with open(filepath, 'r') as f:
        root: ET._Element = ET.parse(f).getroot()
    
    valid_usages = {}

    for child in root:
        assert child.tag == 'valid-usage'

        property_dict = {property.tag: property.text for property in child}

        vu = ValidUsage(name=property_dict['name'], description=property_dict['description'])

        valid_usages[vu.name] = vu
    
    assert len(valid_usages) == len(root)

    return valid_usages
