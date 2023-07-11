from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from lxml import etree as ET


T = TypeVar('T')
U = TypeVar('U')


# TODO: write tests
class Model(ABC, Generic[T, U]):
    
    def __init__(self, metadata: ET._Element):
        self._metadata = metadata

    @property
    def metadata(self) -> ET._Element:
        """Returns the metadata of this model.

        Returns:
            ET._Element: The model's metadata.
        """
        
        return self._metadata
    
    @abstractmethod
    def call(self, inputs: T) -> U:
        """Calls this model with some inputs and returns corresponding output.
        
        The input's type must be the same as specified in the model's manifest file;
        whoever subclasses this class and overrides this method to create a Mercury Extension,
        takes the responsibility to ensure that the expected input & output types of this method
        are exactly the same as specified in the manifest file.

        Args:
            inputs (T): The inputs.

        Returns:
            U: The outputs.
        """
        pass
