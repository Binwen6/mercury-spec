from enum import Enum
from pathlib import Path


class Config(Enum):
    # TODO: this configuration is for TESTING ONLY
    modelCollectionRootPath = Path('../tests/data/sample-model-collection')
