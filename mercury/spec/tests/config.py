from pathlib import Path


class Config:
    specRootDir = Path(__file__).resolve().parent.parent.joinpath('src')
    
    filtersRootDir = specRootDir.joinpath('filters')
    
    callSchemesRootDir = filtersRootDir.joinpath('call-schemes')
    callSchemesMetadataPath = callSchemesRootDir.joinpath('metadata.yml')
    
    tagsRootDir = filtersRootDir.joinpath('tags')
    
    baseModelFilterPath = filtersRootDir.joinpath('base_model.xml')
    
