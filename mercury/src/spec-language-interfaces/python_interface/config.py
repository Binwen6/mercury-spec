from pathlib import Path
from enum import Enum


class Config(Enum):
    installationRootPath = Path(__file__).parent.parent.parent
    specRootPath = installationRootPath.joinpath(Path("spec"))
    
    validUsageRootPath = specRootPath.joinpath(Path("valid-usage"))
    filterSyntaxValidUsageFile = validUsageRootPath.joinpath(Path("filter-syntax.xml"))
    manifestSyntaxValidUsageFile = validUsageRootPath.joinpath(Path("manifest-syntax.xml"))
    
    filterMatchFailureSpecsFile = specRootPath.joinpath(Path("match-filter/match-failures-specs.xml"))

    filtersRootPath = specRootPath.joinpath(Path("filters"))
    baseModelFilterPath = filtersRootPath.joinpath(Path("base_model.xml"))

    pythonBindingRootPath = installationRootPath.joinpath(Path("bindings/python/mercury"))
    
    # TODO: this configuration is for TESTING ONLY
    modelCollectionRootPath = pythonBindingRootPath.joinpath(Path("../tests/data/sample-model-collection"))
