from typing import List, Self, Any, Iterable
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from pathlib import Path

from .filtering import matchFilter
from .spec_interface import FileNames, ManifestUtils
from .config import Config


# TODO: write tests
class ModelCollection:
    @dataclass
    class ModelEntry:
        path: Path
        manifestData: ET.Element

    def __init__(self, entries: List[ModelEntry]):
        self._entries = entries

    @property
    def modelEntries(self) -> List[ModelEntry]:
        return self._entries

    def select(self, filterElement: ET.Element) -> Self:
        return ModelCollection(list(
            entry for entry in self._entries
            if matchFilter(filterElement=filterElement, dataElement=ManifestUtils.getMetadata(entry.manifestData))))


# TODO: write tests
def enumerateAvailableModels() -> ModelCollection:
    """
    Look up the model collection directory and return entries for all available models.
    
    The model collection directory is looked up recursively,
    and any subdirectory containing a manifest file is considered a "leaf" model directory.
    
    Only models with Python implementations are returned.

    Returns:
        ModelCollection: A collection of entries for all available models.
    """

    def join_lists(lists: Iterable[List[Any]]):
        ret = []

        for sub_list in lists:
            ret += sub_list

        return ret

    def enumerateModels(directory: Path) -> List[ModelCollection.ModelEntry]:
        if FileNames.manifestFile in set(directory.iterdir()):
            # we are at a leaf
            return [ModelCollection.ModelEntry(path=directory,
                                               manifestData=ET.parse(
                                                   directory.joinpath(FileNames.manifestFile.value)).getroot())]
        else:
            return join_lists(enumerateModels(sub_dir) for sub_dir in directory.iterdir() if sub_dir.is_dir())

    return ModelCollection(
        [model_entry for model_entry in enumerateModels(Path(Config.modelCollectionRootPath.value))
         if ManifestUtils.supportPythonImplementation(model_entry.manifestData)])
