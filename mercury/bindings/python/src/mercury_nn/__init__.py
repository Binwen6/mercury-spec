from pathlib import Path

from .core import Model
from .model_selection import ModelCollection, enumerateAvailableModels
from .model_creation import instantiateModel

import sys
import os

from .interface import MetadataUtils
from .filtering import Filter

from . import utils

# checks
from . import config
from .config import Config


if Config.specRootPath.value == Path():
    print(
f"""ERROR: The installation directory of Mercury specification is not specified!

Please specify the Mercury specification installation directory in this file: {str(Path(config.__file__).absolute().resolve())}

Note that the Python package you installed with e.g., pip,
is just a Python binding of the Mercury specification,
and it CANNOT work on its own.
You must install the Mercury specification AND the binding
before using Mercury in a specific programming language.
""")

if Config.modelCollectionRootPath.value == Path():
    print(
f"""ERROR: The model collection directory is not specified!
Mercury will NOT be able to access the models you have on your platform!

Please specify the model collection directory in this file: {str(Path(config.__file__).absolute().resolve())}
"""
    )