from dataclasses import dataclass
from pathlib import Path


class InvalidTagException(Exception):
    pass


class InvalidFilterOperationTypeException(Exception):
    pass


class InvalidModelInstanceException(Exception):
    pass


@dataclass
class InvalidModulePathException(Exception):
    """Exception raised when failing to import a module from a path.
    """
    path: Path
