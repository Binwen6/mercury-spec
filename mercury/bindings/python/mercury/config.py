from pathlib import Path
from enum import Enum


class Config(Enum):
    # TODO: this value is for TESTING ONLY
    specRootPath = Path(__file__).resolve().parent.parent.parent.parent.joinpath(Path("spec"))
    
    validUsageRootPath = specRootPath.joinpath(Path("valid-usage"))
    filterSyntaxValidUsageFile = validUsageRootPath.joinpath(Path("filter-syntax.xml"))
    manifestSyntaxValidUsageFile = validUsageRootPath.joinpath(Path("manifest-syntax.xml"))
    
    filterMatchFailureSpecsFile = specRootPath.joinpath(Path("match-filter/match-failures-specs.xml"))

    filtersRootPath = specRootPath.joinpath(Path("filters"))
    baseModelFilterPath = filtersRootPath.joinpath(Path("base_model.xml"))

    pythonBindingRootPath = Path(__file__).resolve().parent
    
    # TODO: this value is for TESTING ONLY
    modelCollectionRootPath = pythonBindingRootPath.parent.joinpath(Path("tests/data/sample-model-collection"))
