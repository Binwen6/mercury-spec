from lxml import etree as ET
from pathlib import Path
from types import ModuleType

import sys
import os

from .specification.interface import TagNames, AttributeNames
from .exceptions import InvalidModulePathException
from importlib.machinery import PathFinder, SourceFileLoader
import importlib.util


# TODO: write tests
def dictElementToDict(dictElement: ET._Element):
    assert dictElement.tag == TagNames.DICT
    
    return {item.attrib[AttributeNames.nameAttribute]: item[0] for item in dictElement}


# TODO: write tests
def moduleFromPath(path: Path) -> ModuleType:
    """Imports a module from a path.
    The module can be either a package with an `__init__.py`, or a single .py script.
    In the former case, `path` should be the path to the package (i.e., the one which contains the `__init__.py`);
    in the latter case, `path` should be the path to the script.

    Args:
        path (Path): The path to the module.

    Raises:
        InvalidModulePathException: Raises when the path is neither a file nor a directory.

    Returns:
        ModuleType: The imported module.
    """
    
    if path.is_file():
        module_name = path.stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    elif path.is_dir():
        module_name = path.name
        spec = importlib.util.spec_from_file_location(module_name, path / '__init__.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        raise InvalidModulePathException(path)
    
    return module
