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


# TODO: write tests
def instantiateModel(modelEntry: ModelCollection.ModelEntry) -> Model:
    implementation_info = ManifestUtils.getImplementationInfo(modelEntry.manifest)

    # import module
    spec = importlib.util.spec_from_file_location("module", str(modelEntry.path.joinpath(implementation_info.sourceFile)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # instantiate model
    model_instance = getattr(module, implementation_info.modelClassName)(manifest=modelEntry.manifest)
    assert isinstance(model_instance, Model)

    return model_instance
