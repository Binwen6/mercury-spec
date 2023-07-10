from lxml import etree as ET
from dataclasses import dataclass
from typing import Dict
from pathlib import Path

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'spec-language-interfaces'))

from python_interface.config import Config


@dataclass
class FilterMatchFailureSpec:
    name: str
    description: str


def loadFilterMatchFailureSpecs(filepath: Path) -> Dict[str, FilterMatchFailureSpec]:
    
    """Loads filter match failure specifications from a file.
    
    The file must be an XML with the following form:
    
    <?xml version="1.0" encoding="UTF-8"?>
    <array>
        <match-failure>
            <name>...</name>
            <description>
                ...
            </description>
        </match-failure>
        
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
    
    filter_match_failure_specs = {}

    for child in root:
        assert child.tag == 'match-failure'

        property_dict = {property.tag: property.text for property in child}

        match_failure = FilterMatchFailureSpec(name=property_dict['name'], description=property_dict['description'])

        filter_match_failure_specs[match_failure.name] = match_failure
    
    assert len(filter_match_failure_specs) == len(root)

    return filter_match_failure_specs
