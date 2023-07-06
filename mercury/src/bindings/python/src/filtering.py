from dataclasses import dataclass
import xml.etree.ElementTree as ET
from enum import Enum
from typing import Self, Sequence

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'spec-language-interfaces'))

from python_interface.interface import (
    TagNames, AttributeNames, FilterOperationTypes, filterXMLfromArgs,
    TypeDeclarationTagNames, TypeDeclarationFilterOperationTypes, TypeDeclarationAttributeNames
)
from .exceptions import InvalidTagException, InvalidFilterOperationTypeException
from .utils import dictElementToDict


# These are tested when testing the `select` method of `ModelCollection`.
@dataclass
class Filter:
    
    filterElement: ET.Element

    @staticmethod
    def fromXML(xmlElement: ET.Element) -> Self:
        """Constructs a filter from an XML element.

        Args:
            xmlElement (ET.Element): The filter XML element.

        Returns:
            Self: The constructed filter.
        """
        
        return Filter(filterElement=xmlElement)
    
    @staticmethod
    def fromArgs(modelType: str | None=None, callScheme: str | None=None, capabilities: Sequence[str] | None=None) -> Self:
        """Constructs a filter from simple arguments.

        Args:
            modelType (str | None): The type of the model. E.g., chat-completion, image-classification, etc.
            callScheme (str | None): The call scheme. E.g., chat-completion, image-classification, etc.
            capabilities (Sequence[str] | None): The required capabilities. E.g., question-answering, math, etc.

        Returns:
            Self: The constructed filter.
        """

        return Filter.fromXML(xmlElement=ET.fromstring(filterXMLfromArgs(
            modelType=modelType, callScheme=callScheme, capabilities=capabilities
        )))


class FilterMatchResult(Enum):
    SUCCESS = 0
    FAILURE = 1


def matchFilter(filterObject: Filter, dataElement: ET.Element) -> FilterMatchResult:
    """
    Match model metadata against a filter.
    Typically, both `filter` and `element` are obtained by parsing an xml document.

    Args:
        filterElement (ET.Element): The filter to match against.
        dataElement (ET.Element): The element to match.
    """
    
    filterElement = filterObject.filterElement

    if dataElement.tag != filterElement.tag:
        return FilterMatchResult.FAILURE

    match filterElement.tag:
        case TagNames.dictType.value:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                case FilterOperationTypes.ALL.value:
                    # match each child element
                    # get all key-value pairs from named-field elements & filters
                    element_children_dict = dictElementToDict(dataElement)
                    filter_children_dict = dictElementToDict(filterElement)

                    if not set(filter_children_dict.keys()).issubset(set(element_children_dict.keys())):
                        return FilterMatchResult.FAILURE

                    return FilterMatchResult.SUCCESS \
                        if all(matchFilter(Filter.fromXML(filter_children_dict[key]), element_children_dict[key])
                               == FilterMatchResult.SUCCESS
                               for key in filter_children_dict.keys()) \
                        else FilterMatchResult.FAILURE
                case FilterOperationTypes.NONE.value:
                    # since tag is compared in the beginning, we can just return success.
                    return FilterMatchResult.SUCCESS
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.listType.value:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                case FilterOperationTypes.ALL.value:
                    if len(dataElement) < len(filterElement):
                        return FilterMatchResult.FAILURE

                    # assume the list is ordered, match each sub-filter v.s. sub-element in order
                    return FilterMatchResult.SUCCESS \
                        if all(matchFilter(Filter.fromXML(sub_filter), sub_element) == FilterMatchResult.SUCCESS
                               for sub_filter, sub_element in zip(filterElement, dataElement)) \
                        else FilterMatchResult.FAILURE
                case FilterOperationTypes.NONE.value:
                    return FilterMatchResult.SUCCESS
        case TagNames.namedField.value:
            # just raise since it should be guaranteed that named field will always be unwrapped before calling `match`
            raise InvalidTagException()
        case TagNames.string.value:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                # TODO: add more filter types for strings, e.g., regular expressions
                case FilterOperationTypes.NONE.value:
                    return FilterMatchResult.SUCCESS
                case FilterOperationTypes.EQUALS.value:
                    return FilterMatchResult.SUCCESS \
                        if dataElement.text == filterElement.text \
                        else FilterMatchResult.FAILURE
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.typeIdentifier.value:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                # TODO: write tests
                case FilterOperationTypes.NONE.value:
                    return FilterMatchResult.SUCCESS
                case FilterOperationTypes.TYPE_MATCH.value:
                    return _matchTypeDeclarationFilter(filterElement[0], dataElement[0])
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.time.value:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                # TODO: add more filter types for time
                case FilterOperationTypes.NONE.value:
                    return FilterMatchResult.SUCCESS
                case _:
                    raise InvalidFilterOperationTypeException()
        case _:
            raise InvalidTagException()


# TODO: add support for comparison filters
def _matchTypeDeclarationFilter(filterElement: ET.Element, dataElement: ET.Element) -> FilterMatchResult:
    """Tests whether `dataElement` matches the requirements specified in `filterElement`.

    Args:
        filterElement (ET.Element): The type declaration (XML element) to be matched.
        dataElement (ET.Element): The filter to be matched against.

    Raises:
        InvalidFilterOperationTypeException: If `filterElement` contains invalid filter operation types (i.e., syntactical error).

    Returns:
        FilterMatchResult: SUCCESS if `dataElement` matches, FAILURE otherwise.
    """
    
    if filterElement.tag != dataElement.tag:
        return FilterMatchResult.FAILURE

    match filterElement.tag:
        # composers: recurse
        case TypeDeclarationTagNames.LIST.value:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    return FilterMatchResult.SUCCESS \
                        if _matchTypeDeclarationFilter(filterElement[0], dataElement[0]) == FilterMatchResult.SUCCESS \
                        else FilterMatchResult.FAILURE
                case TypeDeclarationFilterOperationTypes.NONE.value:
                    return FilterMatchResult.SUCCESS
                case _:
                    raise InvalidFilterOperationTypeException()
                
        case TypeDeclarationTagNames.TUPLE.value:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    return FilterMatchResult.SUCCESS \
                        if len(filterElement) == len(dataElement) and \
                            all(_matchTypeDeclarationFilter(sub_filter, sub_element) == FilterMatchResult.SUCCESS
                                for sub_filter, sub_element in zip(filterElement, dataElement)) \
                        else FilterMatchResult.FAILURE
                case TypeDeclarationFilterOperationTypes.NONE.value:
                    return FilterMatchResult.SUCCESS
                case _:
                    raise InvalidFilterOperationTypeException()

        # primitives: check
        case TypeDeclarationTagNames.STRING.value | TypeDeclarationTagNames.BOOL.value:
            # type checked at beginning of function; so can return SUCCESS directly.
            return FilterMatchResult.SUCCESS

        # there are more possible filter operation types for tensor
        case TypeDeclarationTagNames.TENSOR.value:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                # ndim-equals requires the number of dimensions to match
                case TypeDeclarationFilterOperationTypes.NDIM_EQUALS.value:
                    return FilterMatchResult.SUCCESS \
                        if len(filterElement) == len(dataElement) \
                        else FilterMatchResult.FAILURE
                # shape-equals requires the shapes to be exactly the same
                case TypeDeclarationFilterOperationTypes.SHAPE_EQUALS.value:
                    return FilterMatchResult.SUCCESS \
                        if len(filterElement) == len(dataElement) and \
                            all(int(dim_filter.text.strip()) == int(dim_data.text.strip())
                                for dim_filter, dim_data in zip(filterElement, dataElement)) \
                        else FilterMatchResult.FAILURE
                case TypeDeclarationFilterOperationTypes.NONE.value:
                    return FilterMatchResult.SUCCESS
                case _:
                    raise InvalidFilterOperationTypeException()

        # there are more possibilities for named-value-collection
        case TypeDeclarationTagNames.NAMED_VALUE_COLLECTION.value:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    # "all" means that the key names are exactly the same in the context of a named value collection.
                    filter_key_names = {sub_element.attrib[TypeDeclarationAttributeNames.namedValueNameAttributeName.value]
                                        for sub_element in filterElement}
                    data_key_names = {sub_element.attrib[TypeDeclarationAttributeNames.namedValueNameAttributeName.value]
                                        for sub_element in dataElement}
                    
                    return FilterMatchResult.SUCCESS if filter_key_names == data_key_names else FilterMatchResult.FAILURE
                case TypeDeclarationFilterOperationTypes.NONE.value:
                    return FilterMatchResult.SUCCESS
                case _:
                    raise InvalidFilterOperationTypeException()
        case _:
            raise InvalidTagException()