from typing import Any
import xml.etree.ElementTree as ET
from pathlib import Path
import importlib.util

from .model_selection import ModelCollection
from .exceptions import InvalidModelInstanceException
from .core import Model

import sys
import os
from .specification.interface import ManifestUtils
from .utils import moduleFromPath


def instantiateModel(modelEntry: ModelCollection.ModelEntry) -> Model:
    implementation_info = ManifestUtils.getImplementationInfo(modelEntry.manifest)

    # import module
    module = moduleFromPath(modelEntry.path.joinpath(implementation_info.modulePath))

    # instantiate model
    model_instance = getattr(module, implementation_info.modelClassName)(manifest=modelEntry.manifest)

    return model_instance
