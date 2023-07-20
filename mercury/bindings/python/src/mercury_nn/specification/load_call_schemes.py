from ..filtering import Filter
from ..config import Config

from typing import Dict
from lxml import etree as ET
import yaml
from pathlib import Path


def loadCallSchemes() -> Dict[str, Filter]:
    """
    Load the call schemes from the call schemes directory.

    Returns:
        dict: A dictionary containing the call schemes.
              The keys are the scheme names, and the values are instances of the Filter class.
    """
    
    with open(Config.callSchemesMetadataPath, 'r') as f:
        metadata = yaml.safe_load(f)
    
    return {key: Filter.fromXMLElement(ET.parse(Config.callSchemesRootPath.joinpath(value)).getroot()) for key, value in metadata.items()}