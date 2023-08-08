from dataclasses import dataclass
from lxml import etree as ET
from enum import Enum, auto
from typing import Self, Sequence, Tuple, Iterable, Dict, List

import sys
import os

from .specification.interface import (
    TagNames, AttributeNames, FilterOperationTypes, filterXMLfromArgs,
    TypeDeclarationTagNames, TypeDeclarationFilterOperationTypes, TypeDeclarationAttributeNames,
    FilterMatchFailureType
)
from .specification.load_tags import loadTags
from .specification.constants import BOOLEAN_TRUE_VALUES, BOOLEAN_FALSE_VALUES, UNFILLED_VALUE_PLACEHOLDER
from .tag_matching import parseCondensedTags, InvalidCondensedTagsException

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
    def fromArgs(callSchemes: Iterable[str] | None=None) -> Self:
        """Constructs a filter from simple arguments.

        Args:
            callSchemes (Iterable[str] | None): The call scheme. E.g., chat-completion, image-classification, etc.

        Returns:
            Self: The constructed filter.
        """

        return Filter.fromXMLElement(xmlElement=ET.fromstring(filterXMLfromArgs(
            callSchemes=callSchemes
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

            # TODO: write tests for this
            tagStack: List[str]
            
            def __eq__(self, __value: Self) -> bool:
                return self.filtererLine == __value.filtererLine and self.filtereeLine == __value.filtereeLine and self.tagStack == __value.tagStack
        
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


def matchFilter(filterObject: Filter, dataElement: ET._Element, loadedTags: Dict[str, ET._Element] | None=None) -> FilterMatchResult:
    """
    Match model manifest against a filter.
    Typically, both `filter` and `element` are obtained by parsing an xml document.
    
    NOTE: The validity of arguments are NOT checked.

    Args:
        filterElement (ET._Element): The filter to match against.
        dataElement (ET._Element): The element to match.
        loadedTags (Dict[str, ET._Element] | None): The loaded tags.
            Passing a cached obtained by `loadTags()` will improve the speed of this function by avoiding (re-)loading the tags.
    """
    
    if loadedTags is None:
        loadedTags = loadTags()
    
    return _matchFilterElement(filterObject.filterElement, dataElement, dataElement, [], loadedTags)
    

def _matchFilterElement(filterElement: ET._Element,
                dataElement: ET._Element,
                rootElement: ET._Element,
                currentStack: List[str],
                loadedTags: Dict[str, ET._Element]) -> FilterMatchResult:
    
    # convenient objects
    failurePosition = _FailurePosition(
        filtererLine=filterElement.sourceline,
        filtereeLine=dataElement.sourceline,
        tagStack=currentStack
    )


    match filterElement.tag:
        case TagNames.DICT:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )
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
                        _matchFilterElement(filter_children_dict[key], element_children_dict[key], rootElement, currentStack, loadedTags)
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
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case FilterOperationTypes.ALL:
                    if len(dataElement) < len(filterElement):
                        # insufficient list children
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.LIST_INSUFFICIENT_CHILDREN,
                            failurePosition=failurePosition
                        )
                    
                    children_match_results = [
                        _matchFilterElement(sub_filter, sub_element, rootElement, currentStack, loadedTags)
                        for sub_filter, sub_element in zip(filterElement, dataElement)
                    ]

                    # assume the list is ordered, match each sub-filter v.s. sub-element in order
                    return _result_from_children_results(children_match_results)
                case FilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.LOGICAL:
            sub_results = [_matchFilterElement(sub_filter, dataElement, rootElement, currentStack, loadedTags) for sub_filter in filterElement]

            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case FilterOperationTypes.AND:
                    if not all(sub_result.isSuccess for sub_result in sub_results):
                        return _get_first_failured_child_match(sub_results)
                    
                    return FilterMatchResult.success()
                case FilterOperationTypes.OR:
                    if not any(sub_result.isSuccess for sub_result in sub_results):
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.LOGICAL_OPERATION_MATCH_FAILURE,
                            failurePosition=failurePosition
                        )
                    
                    return FilterMatchResult.success()
                case FilterOperationTypes.NOT:
                    if sub_results[0].isSuccess:
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.LOGICAL_OPERATION_MATCH_FAILURE,
                            failurePosition=failurePosition
                        )
                    
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
            
        case TagNames.TAG_COLLECTION:
            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case FilterOperationTypes.IMPLICIT_TAG_MATCH:
                    # for implicit match, the tag is considered to match as long as the filter matches
                    tag_sets = [parseCondensedTags(sub_element.text) for sub_element in filterElement]
                    tags = set()

                    for tag_set in tag_sets:
                        tags.update(tag_set)

                    children_match_results = [_matchFilterElement(loadedTags[tag], rootElement, rootElement, currentStack + [tag], loadedTags) for tag in tags]

                    # TODO: add more information to indicate which tag is being matched when the error occurs,
                    # and how we came to match that tag.
                    return _result_from_children_results(children_match_results)

                case FilterOperationTypes.EXPLICIT_TAG_MATCH:
                    # for explicit match, the tag matches only if the tag explicitly appears in the tag collection
                    # first we need to parse the condensed tags
                    filter_tag_sets = [parseCondensedTags(sub_element.text) for sub_element in filterElement]
                    data_tag_sets = [parseCondensedTags(sub_element.text) for sub_element in dataElement]

                    filter_tags, data_tags = set(), set()
                    for tag_set in filter_tag_sets:
                        filter_tags.update(tag_set)
                    
                    for tag_set in data_tag_sets:
                        data_tags.update(tag_set)

                    if not filter_tags.issubset(data_tags):
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.TAG_COLLECTION_EXPLICIT_TAG_MATCH_FAILURE,
                            failurePosition=failurePosition
                        )
                    
                    return FilterMatchResult.success()
                
                case FilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
            
        case TagNames.NAMED_FIELD:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

            # just raise since it should be guaranteed that named field will always be unwrapped before calling `match`
            raise InvalidTagException()
        case TagNames.STRING:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

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
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case FilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case FilterOperationTypes.TYPE_MATCH:
                    return _matchFilterElement(filterElement[0], dataElement[0], rootElement, currentStack, loadedTags)
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.BOOL:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                # TODO: add more filter types for bool, e.g., regular expressions
                case FilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                
                case FilterOperationTypes.EQUALS:
                    if dataElement.text.strip() == UNFILLED_VALUE_PLACEHOLDER:
                       return FilterMatchResult.failure(
                            failureType=_FailureTypes.BOOL_VALUE_NOT_EQUAL,
                            failurePosition=failurePosition
                        )
                        
                    filter_value = True if filterElement.text.strip() in BOOLEAN_TRUE_VALUES else False
                    data_value = True if dataElement.text.strip() in BOOLEAN_TRUE_VALUES else False
                    
                    return FilterMatchResult.success() if filter_value == data_value \
                        else FilterMatchResult.failure(
                            failureType=_FailureTypes.BOOL_VALUE_NOT_EQUAL,
                            failurePosition=failurePosition
                        )
                        
                case _:
                    raise InvalidFilterOperationTypeException()
        
        case TagNames.INT:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )
            
            is_comparison = filterElement.attrib[AttributeNames.filterOperationTypeAttribute] in (
                FilterOperationTypes.EQUALS,
                FilterOperationTypes.LESS_THAN,
                FilterOperationTypes.LESS_THAN_OR_EQUALS,
                FilterOperationTypes.GREATER_THAN,
                FilterOperationTypes.GREATER_THAN_OR_EQUALS
            )
            
            if is_comparison:
                failed_comparison = FilterMatchResult.failure(
                    failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                    failurePosition=failurePosition
                )
                
                if dataElement.text.strip() == UNFILLED_VALUE_PLACEHOLDER:
                    return failed_comparison
                
                filter_value, data_value = int(filterElement.text.strip()), int(dataElement.text.strip())
                
                match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                    case FilterOperationTypes.EQUALS:
                        return FilterMatchResult.success() \
                            if data_value == filter_value \
                            else failed_comparison
                    case FilterOperationTypes.LESS_THAN:
                        return FilterMatchResult.success() \
                            if data_value < filter_value \
                            else failed_comparison
                    case FilterOperationTypes.LESS_THAN_OR_EQUALS:
                        return FilterMatchResult.success() \
                            if data_value <= filter_value \
                            else failed_comparison
                    case FilterOperationTypes.GREATER_THAN:
                        return FilterMatchResult.success() \
                            if data_value > filter_value \
                            else failed_comparison
                    case FilterOperationTypes.GREATER_THAN_OR_EQUALS:
                        return FilterMatchResult.success() \
                            if data_value >= filter_value \
                            else failed_comparison
            else:
                match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                    case FilterOperationTypes.NONE:
                        return FilterMatchResult.success()
                    case _:
                        raise InvalidFilterOperationTypeException()
                
        case TagNames.FLOAT:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )
            
            is_comparison = filterElement.attrib[AttributeNames.filterOperationTypeAttribute] in (
                FilterOperationTypes.EQUALS,
                FilterOperationTypes.LESS_THAN,
                FilterOperationTypes.LESS_THAN_OR_EQUALS,
                FilterOperationTypes.GREATER_THAN,
                FilterOperationTypes.GREATER_THAN_OR_EQUALS
            )
            
            if is_comparison:
                failed_comparison = FilterMatchResult.failure(
                    failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                    failurePosition=failurePosition
                )
                
                if dataElement.text.strip() == UNFILLED_VALUE_PLACEHOLDER:
                    return failed_comparison

                filter_value, data_value = float(filterElement.text.strip()), float(dataElement.text.strip())

                match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                    case FilterOperationTypes.EQUALS:
                        return FilterMatchResult.success() \
                            if data_value == filter_value \
                            else failed_comparison
                    case FilterOperationTypes.LESS_THAN:
                        return FilterMatchResult.success() \
                            if data_value < filter_value \
                            else failed_comparison
                    case FilterOperationTypes.LESS_THAN_OR_EQUALS:
                        return FilterMatchResult.success() \
                            if data_value <= filter_value \
                            else failed_comparison
                    case FilterOperationTypes.GREATER_THAN:
                        return FilterMatchResult.success() \
                            if data_value > filter_value \
                            else failed_comparison
                    case FilterOperationTypes.GREATER_THAN_OR_EQUALS:
                        return FilterMatchResult.success() \
                            if data_value >= filter_value \
                            else failed_comparison
            else:
                match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                    case FilterOperationTypes.NONE:
                        return FilterMatchResult.success()
                    case _:
                        raise InvalidFilterOperationTypeException()
        
        # composers: recurse
        case TypeDeclarationTagNames.LIST:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    return _matchFilterElement(filterElement[0], dataElement[0], rootElement, currentStack, loadedTags)
                case TypeDeclarationFilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
                
        case TypeDeclarationTagNames.TUPLE:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    if len(filterElement) != len(dataElement):
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.TYPE_DECLARATION_TUPLE_INCORRECT_CHILDREN_COUNT,
                            failurePosition=failurePosition
                        )
                    
                    children_match_results = [
                        _matchFilterElement(sub_filter, sub_element, rootElement, currentStack, loadedTags)
                        for sub_filter, sub_element in zip(filterElement, dataElement)
                    ]

                    return _result_from_children_results(children_match_results)
                
                case TypeDeclarationFilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()

        # primitives: check
        case TypeDeclarationTagNames.STRING | TypeDeclarationTagNames.BOOL:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

            # type checked at beginning of function; so can return SUCCESS directly.
            return FilterMatchResult.success()

        # there are more possible filter operation types for tensor
        case TypeDeclarationTagNames.TENSOR:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

            match filterElement.attrib[AttributeNames.filterOperationTypeAttribute]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    if len(filterElement) != len(dataElement):
                        # Tensor filters requires that number of dims must match exactly
                        return FilterMatchResult.failure(
                            failureType=_FailureTypes.TYPE_DECLARATION_TENSOR_DIFFERENT_DIM_NUMBER,
                            failurePosition=failurePosition
                        )
                    
                    children_match_results = [
                        _matchFilterElement(sub_filter, sub_element, rootElement, currentStack, loadedTags)
                        for sub_filter, sub_element in zip(filterElement, dataElement)
                    ]
                    
                    return _result_from_children_results(children_match_results)

                case TypeDeclarationFilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
        
        case TypeDeclarationTagNames.DIM:
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

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
            if dataElement.tag != filterElement.tag:
                return FilterMatchResult.failure(
                    failureType=_FailureTypes.TAG_MISMATCH,
                    failurePosition=failurePosition
                )

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
                        _matchFilterElement(filter_children_dict[key], data_children_dict[key], rootElement, currentStack, loadedTags)
                        for key in filter_children_dict.keys()
                    ]
                    
                    return _result_from_children_results(children_match_results)

                case TypeDeclarationFilterOperationTypes.NONE:
                    return FilterMatchResult.success()
                case _:
                    raise InvalidFilterOperationTypeException()
                
        case _:
            raise InvalidTagException()
