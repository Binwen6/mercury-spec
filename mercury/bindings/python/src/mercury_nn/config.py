from pathlib import Path


class Config:
    # TODO: this value is for TESTING ONLY
    specRootPath = Path(__file__).resolve().parent.parent.parent.parent.parent.joinpath('spec/src')
    # Set the Mercury specification installation directory below in form of Path('<mercury-specification-installation-path>')
    # use ABSOLUTE path.
    # specRootPath = Path('')
    
    validUsageRootPath = specRootPath.joinpath('valid-usage')
    filterSyntaxValidUsageFile = validUsageRootPath.joinpath('filter-syntax.xml')
    manifestSyntaxValidUsageFile = validUsageRootPath.joinpath('manifest-syntax.xml')
    
    filterMatchFailureSpecsFile = specRootPath.joinpath('match-filter/match-failures-specs.xml')

    filtersRootPath = specRootPath.joinpath('filters')
    baseModelFilterPath = filtersRootPath.joinpath('base_model.xml')

    callSchemesRootPath = filtersRootPath.joinpath('call-schemes')
    callSchemesMetadataPath = callSchemesRootPath.joinpath('metadata.yml')

    pythonBindingRootPath = Path(__file__).resolve().parent
    
    # TODO: this value is for TESTING ONLY
    modelCollectionRootPath = pythonBindingRootPath.parent.parent.parent.parent.parent.joinpath('sample-model-collection')
    # Set the model collection directory below in form of Path('<model-collection-directory>')
    # use ABSOLUTE path.
    # modelCollectionRootPath = Path('')
