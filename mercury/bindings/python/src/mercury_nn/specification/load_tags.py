from ..config import Config

from typing import Dict
from lxml import etree as ET
import yaml
from pathlib import Path


def loadTags() -> Dict[str, ET._Element]:
    """
    Load the tags from the call schemes directory.

    Returns:
        dict: A dictionary containing the tags.
              The keys are the tag names, and the values are the tag filters in parsed XML form.
    """
    
    with open(Config.tagsMetadataPath, 'r') as f:
        metadata = yaml.safe_load(f)
    
    return {key: ET.parse(Config.tagsRootPath.joinpath(value)).getroot() for key, value in metadata.items()}