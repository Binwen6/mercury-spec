from dataclasses import dataclass
from lxml import etree as ET
from enum import Enum, auto
from typing import Self, Sequence, Tuple, Iterable

import sys
import os

from .specification.interface import (
    TagNames, AttributeNames, FilterOperationTypes, filterXMLfromArgs,
    TypeDeclarationTagNames, TypeDeclarationFilterOperationTypes, TypeDeclarationAttributeNames,
    FilterMatchFailureType
)
from .exceptions import InvalidTagException, InvalidFilterOperationTypeException
from .utils import dictElementToDict


# These are tested when testing the `select` method of `ModelCollection`.
@dataclass
class Filter:
    
    filterElement: ET._Element

    @staticmethod
    def fromXMLElement(xmlElement: ET._Element) -> Self:
        """Constructs a filter from an XML element.

        Args:
            xmlElement (ET._Element): The filter XML element.

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

        return Filter.fromXMLElement(xmlElement=ET.fromstring(filterXMLfromArgs(
            modelType=modelType, callScheme=callScheme, capabilities=capabilities
        )))


@dataclass
class FilterMatchResult:

    class ResultType(Enum):
        SUCCESS = auto()
        FAILURE = auto()
    
    @dataclass
    class FailureInfo:
        
        
        @dataclass
        class FailurePosition:
            filtererLine: int
            filtereeLine: int
            
            def __eq__(self, __value: Self) -> bool:
                return self.filtererLine == __value.filtererLine and self.filtereeLine == __value.filtereeLine
        
        failureType: FilterMatchFailureType
        failurePosition: FailurePosition
        
        def __eq__(self, __value: Self) -> bool:
            return self.failureType == __value.failureType and self.failurePosition == __value.failurePosition
    
    resultType: ResultType
    failureInfo: FailureInfo | None

    @property
    def isSuccess(self) -> bool:
        return self.resultType == FilterMatchResult.ResultType.SUCCESS

    @staticmethod
    def success() -> Self:
        return FilterMatchResult(
            resultType=FilterMatchResult.ResultType.SUCCESS,
            failureInfo=None
        )
    
    @staticmethod
    def failure(failureType, failurePosition) -> Self:
        """
        `failureType` and `failurePosition` must match the types specified in `FailureInfo`
        """
        return FilterMatchResult(
            resultType=FilterMatchResult.ResultType.FAILURE,
            failureInfo=FilterMatchResult.FailureInfo(
                failureType=failureType,
                failurePosition=failurePosition
            )
        )
    
    def __eq__(self, __value: Self) -> bool:
        if self.resultType != __value.resultType:
            return False
        
        match self.resultType:
            case FilterMatchResult.ResultType.SUCCESS:
                return True
            case FilterMatchResult.ResultType.FAILURE:
                return self.failureInfo == __value.failureInfo
    
    
# convenient classes
_FailureInfo = FilterMatchResult.FailureInfo
_FailureTypes = FilterMatchFailureType
_FailurePosition = FilterMatchResult.FailureInfo.FailurePosition

# convenient methods
_all_children_match_successful = lambda children_match_results: all(result.isSuccess for result in children_match_results)
_get_first_failured_child_match = lambda children_match_results: next(iter(filter(lambda x: not x.isSuccess, children_match_results)))
_result_from_children_results = \
    lambda children_match_results: FilterMatchResult.success() \
        if _all_children_match_successful(children_match_results) \
        else _get_first_failured_child_match(children_match_results)
    

def matchFilter(filterObject: Filter, dataElement: ET._Element) -> FilterMatchResult:
    """
    Match model metadata against a filter.
    Typically, both `filter` and `element` are obtained by parsing an xml document.
    
    NOTE: The validity of arguments are NOT checked.

    Args:
        filterElement (ET._Element): The filter to match against.
        dataElement (ET._Element): The element to match.
    """
    
    filterElement = filterObject.filterElement
    
    # convenient objects
    failurePosition = _FailurePosition(
        filtererLine=filterElement.sourceline,
        filtereeLine=dataElement.sourceline
    )

    if dataElement.tag != filterElement.tag:
        return FilterMatchResult.failure(
            failureType=_FailureTypes.TAG_MISMATCH,
            failurePosition=failurePosition
        )

    match filterElement.tag:
        case TagNames.DICT:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case FilterOperationTypes.ALL:
                    # match each child element
                    # get all key-value pairs from named-field elements & filters
                    element_children_dict = dictElementToDict(dataElement)
                    filter_children_dict = dictElementToDict(filterElement)

                    if not set(filter_children_dict.keys()).issubset(set(element_children_dict.keys())):
                        # missing key
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.DICT_MISSING_KEY,
                            failurePosition=failurePosition
                        )

                    children_match_results = [
                        matchFilter(Filter.fromXMLElement(filter_children_dict[key]), element_children_dict[key])
                        for key in filter_children_dict.keys()
                    ]
                    
                    return FilterMatchResult.success() \
                        if _all_children_match_successful(children_match_results) \
                        else _get_first_failured_child_match(children_match_results)
                case FilterOperationTypes.NONE:
                    # since tag is compared in the beginning, we can just return success.
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.LIST:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case FilterOperationTypes.ALL:
                    if len(dataElement) < len(filterElement):
                        # insufficient list children
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.LIST_INSUFFICIENT_CHILDREN,
                            failurePosition=failurePosition
                        )
                    
                    children_match_results = [
                        matchFilter(Filter.fromXMLElement(sub_filter), sub_element)
                        for sub_filter, sub_element in zip(filterElement, dataElement)
                    ]

                    # assume the list is ordered, match each sub-filter v.s. sub-element in order
                    return _result_from_children_results(children_match_results)
                case FilterOperationTypes.NONE:
                    return FilterMatchResult.success()
        case TagNames.NAMED_FIELD:
            # just raise since it should be guaranteed that named field will always be unwrapped before calling `match`
            raise InvalidTagException()
        case TagNames.STRING:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                # TODO: add more filter types for strings, e.g., regular expressions
                case FilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case FilterOperationTypes.EQUALS:
                    return FilterMatchResult.success() \
                        if dataElement.text == filterElement.text \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.STRING_VALUE_NOT_EQUAL,
                            failurePosition=failurePosition
                        )
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.TYPE_DECLARATION:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case FilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case FilterOperationTypes.TYPE_MATCH:
                    return _matchTypeDeclarationFilter(filterElement[0], dataElement[0])
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.BOOL:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                # TODO: add more filter types for bool, e.g., regular expressions
                case FilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
        
        case TagNames.INT:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case FilterOperationTypes.EQUALS:
                    return FilterMatchResult.success() \
                        if int(dataElement.text.strip()) == int(filterElement.text.strip()) \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                            failurePosition=failurePosition
                        )
                case FilterOperationTypes.LESS_THAN:
                    return FilterMatchResult.success() \
                        if int(dataElement.text.strip()) < int(filterElement.text.strip()) \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                            failurePosition=failurePosition
                        )
                case FilterOperationTypes.LESS_THAN_OR_EQUALS:
                    return FilterMatchResult.success() \
                        if int(dataElement.text.strip()) <= int(filterElement.text.strip()) \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                            failurePosition=failurePosition
                        )
                case FilterOperationTypes.GREATER_THAN:
                    return FilterMatchResult.success() \
                        if int(dataElement.text.strip()) > int(filterElement.text.strip()) \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                            failurePosition=failurePosition
                        )
                case FilterOperationTypes.GREATER_THAN_OR_EQUALS:
                    return FilterMatchResult.success() \
                        if int(dataElement.text.strip()) >= int(filterElement.text.strip()) \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                            failurePosition=failurePosition
                        )
                case _:
                    raise InvalidFilterOperationTypeException()
                
        case TagNames.FLOAT:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case FilterOperationTypes.EQUALS:
                    return FilterMatchResult.success() \
                        if float(dataElement.text.strip()) == float(filterElement.text.strip()) \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                            failurePosition=failurePosition
                        )
                case FilterOperationTypes.LESS_THAN:
                    return FilterMatchResult.success() \
                        if float(dataElement.text.strip()) < float(filterElement.text.strip()) \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                            failurePosition=failurePosition
                        )
                case FilterOperationTypes.LESS_THAN_OR_EQUALS:
                    return FilterMatchResult.success() \
                        if float(dataElement.text.strip()) <= float(filterElement.text.strip()) \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                            failurePosition=failurePosition
                        )
                case FilterOperationTypes.GREATER_THAN:
                    return FilterMatchResult.success() \
                        if float(dataElement.text.strip()) > float(filterElement.text.strip()) \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                            failurePosition=failurePosition
                        )
                case FilterOperationTypes.GREATER_THAN_OR_EQUALS:
                    return FilterMatchResult.success() \
                        if float(dataElement.text.strip()) >= float(filterElement.text.strip()) \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                            failurePosition=failurePosition
                        )
                case _:
                    raise InvalidFilterOperationTypeException()
        case _:
            raise InvalidTagException()


def _matchTypeDeclarationFilter(filterElement: ET._Element, dataElement: ET._Element) -> FilterMatchResult:
    """Tests whether `dataElement` matches the requirements specified in `filterElement`.

    NOTE: The validity of arguments are NOT checked.

    Args:
        filterElement (ET._Element): The type declaration (XML element) to be matched.
        dataElement (ET._Element): The filter to be matched against.

    Raises:
        InvalidFilterOperationTypeException: If `filterElement` contains invalid filter operation types (i.e., syntactical error).

    Returns:
        FilterMatchResult: SUCCESS if `dataElement` matches, FAILURE otherwise.
    """

    # convenient objects
    failurePosition = _FailurePosition(
        filtererLine=filterElement.sourceline,
        filtereeLine=dataElement.sourceline
    )
    
    if filterElement.tag != dataElement.tag:
        return FilterMatchResult.failure(
            failureType=_FailureTypes.TAG_MISMATCH,
            failurePosition=failurePosition
        )

    match filterElement.tag:
        # composers: recurse
        case TypeDeclarationTagNames.LIST:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    return _matchTypeDeclarationFilter(filterElement[0], dataElement[0])
                case TypeDeclarationFilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
                
        case TypeDeclarationTagNames.TUPLE:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    if len(filterElement) != len(dataElement):
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.TYPE_DECLARATION_TUPLE_INCORRECT_CHILDREN_COUNT,
                            failurePosition=failurePosition
                        )
                    
                    children_match_results = [
                        _matchTypeDeclarationFilter(sub_filter, sub_element)
                        for sub_filter, sub_element in zip(filterElement, dataElement)
                    ]

                    return _result_from_children_results(children_match_results)
                
                case TypeDeclarationFilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()

        # primitives: check
        case TypeDeclarationTagNames.STRING | TypeDeclarationTagNames.BOOL:
            # type checked at beginning of function; so can return SUCCESS directly.
            return FilterMatchResult.success()

        # there are more possible filter operation types for tensor
        case TypeDeclarationTagNames.TENSOR:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    if len(filterElement) != len(dataElement):
                        # Tensor filters requires that number of dims must match exactly
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.TYPE_DECLARATION_TENSOR_DIFFERENT_DIM_NUMBER,
                            failurePosition=failurePosition
                        )
                    
                    children_match_results = [
                        _matchTypeDeclarationFilter(sub_filter, sub_element)
                        for sub_filter, sub_element in zip(filterElement, dataElement)
                    ]
                    
                    return _result_from_children_results(children_match_results)

                case TypeDeclarationFilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
        
        case TypeDeclarationTagNames.DIM:
            filterOp = filterElement.attrib[AttributeNames.filterOperationTypeAttribute]
            
            if filterOp == TypeDeclarationFilterOperationTypes.NONE:
                return FilterMatchResult.success()
            
            # we are counting on the `int()` function to raise exceptions
            # if the dimension specified is not a valid integer
            filterDim = int(filterElement.text.strip())
            dataDim = int(dataElement.text.strip())
            
            # convenient object
            failure = FilterMatchResult.failure(
                failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
                failurePosition=failurePosition
            )

            match filterOp:
                case TypeDeclarationFilterOperationTypes.EQUALS:
                    return FilterMatchResult.success() if dataDim == filterDim else failure
                case TypeDeclarationFilterOperationTypes.LESS_THAN:
                    return FilterMatchResult.success() if dataDim < filterDim else failure
                case TypeDeclarationFilterOperationTypes.LESS_THAN_OR_EQUALS:
                    return FilterMatchResult.success() if dataDim <= filterDim else failure
                case TypeDeclarationFilterOperationTypes.GREATER_THAN:
                    return FilterMatchResult.success() if dataDim > filterDim else failure
                case TypeDeclarationFilterOperationTypes.GREATER_THAN_OR_EQUALS:
                    return FilterMatchResult.success() if dataDim >= filterDim else failure
                case _:
                    raise InvalidFilterOperationTypeException()

        # there are more possibilities for named-value-collection
        case TypeDeclarationTagNames.NAMED_VALUE_COLLECTION:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    # "all" means that the key names are exactly the same in the context of a named value collection.
                    filter_children_dict = {
                        sub_element.attrib[TypeDeclarationAttributeNames.namedValueNameAttributeName]: sub_element[0]
                        for sub_element in filterElement
                    }
                    
                    data_children_dict = {
                        sub_element.attrib[TypeDeclarationAttributeNames.namedValueNameAttributeName]: sub_element[0]
                        for sub_element in dataElement
                    }
                    
                    if set(filter_children_dict.keys()) != set(data_children_dict.keys()):
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DIFFERENT_KEYS,
                            failurePosition=failurePosition
                        )
                    
                    children_match_results = [
                        _matchTypeDeclarationFilter(filter_children_dict[key], data_children_dict[key])
                        for key in filter_children_dict.keys()
                    ]
                    
                    return _result_from_children_results(children_match_results)

                case TypeDeclarationFilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
        
        case _:
            raise InvalidTagException()