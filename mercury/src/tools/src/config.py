from pathlib import Path
from enum import Enum


class Config(Enum):
    specRootPath = Path(__file__).parent.parent.parent.joinpath("spec")
    validUsageRootPath = specRootPath.joinpath("valid-usage")
    filterSyntaxValidUsageFile = validUsageRootPath.joinpath("filter-syntax.xml")
    manifestSyntaxValidUsageFile = validUsageRootPath.joinpath('manifest-syntax.xml')
