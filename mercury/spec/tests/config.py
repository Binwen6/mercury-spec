from pathlib import Path


class Config:
    specRootDir = Path(__file__).resolve().parent.parent.joinpath('src')
    
    filtersRootDir = specRootDir.joinpath('filters')
    
    tagsRootDir = filtersRootDir.joinpath('tags')
    tagsMetadataPath = tagsRootDir.joinpath('metadata.yml')
    
    baseModelFilterPath = filtersRootDir.joinpath('base_model.xml')
    
