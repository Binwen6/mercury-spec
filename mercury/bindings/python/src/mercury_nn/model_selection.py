from typing import List, Self, Any, Iterable
from dataclasses import dataclass
from lxml import etree as ET
from pathlib import Path

from .filtering import matchFilter, FilterMatchResult, Filter

import sys
import os

from .specification.interface import FileNames, ManifestUtils
from .config import Config


class ModelCollection:
    @dataclass
    class ModelEntry:
        path: Path
        metadata: ET._Element

    def __init__(self, entries: List[ModelEntry]):
        self._entries = entries

    def __iter__(self) -> List[ModelEntry]:
        return iter(self._entries)
    
    def __getitem__(self, index):
        return self._entries[index]

    @property
    def modelEntries(self) -> List[ModelEntry]:
        return self._entries

    def select(self, filterObject: Filter) -> Self:
        return ModelCollection(list(
            entry for entry in self._entries
            if matchFilter(filterObject=filterObject,
                           dataElement=ManifestUtils.getModelSpecs(entry.metadata))
                .isSuccess))


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
        if FileNames.manifestFile in set(Path(path.name) for path in directory.iterdir()):
            # we are at a leaf
            return [ModelCollection.ModelEntry(path=directory,
                                               metadata=ET.parse(
                                                   directory.joinpath(FileNames.manifestFile)).getroot())]
        else:
            return join_lists(enumerateModels(sub_dir) for sub_dir in directory.iterdir() if sub_dir.is_dir())

    return ModelCollection(
        [model_entry for model_entry in enumerateModels(Path(Config.modelCollectionRootPath))
         if ManifestUtils.supportPythonImplementation(model_entry.metadata)])
