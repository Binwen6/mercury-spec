from dataclasses import dataclass
from enum import Enum, auto
from typing import Self, Iterable, Dict, Union, Tuple, Set, List, Any

from lxml import etree as ET

import sys
import os

from ..specification.interface import (
    TagNames, AttributeNames, FilterOperationTypes, filterXMLfromArgs,
    TypeDeclarationTagNames, TypeDeclarationFilterOperationTypes, TypeDeclarationAttributeNames,
    FilterSyntaxInvalidityType
)
from ..specification.load_tags import loadTags
from ..tag_matching import parseCondensedTags, InvalidCondensedTagsException


@dataclass
class SyntaxValidationResult:
    
    class ResultType(Enum):
        VALID = auto()
        INVALID = auto()
        
    @dataclass
    class InvalidityInfo:
            
        @dataclass
        class InvalidityPosition:
            line: int

            def __eq__(self, __value: Self) -> bool:
                return self.line == __value.line
        
        invalidityType: FilterSyntaxInvalidityType
        invalidityPosition: InvalidityPosition

        def __eq__(self, __value: Self) -> bool:
            return self.invalidityType == __value.invalidityType and self.invalidityPosition == __value.invalidityPosition

    resultType: ResultType
    invalidityInfo: InvalidityInfo | None

    @property
    def isValid(self) -> bool:
        return self.resultType == SyntaxValidationResult.ResultType.VALID
    
    @staticmethod
    def valid() -> Self:
        return SyntaxValidationResult(
            resultType=SyntaxValidationResult.ResultType.VALID,
            invalidityInfo=None
        )
    
    @staticmethod
    def invalid(invalidityType, invalidityPosition) -> Self:
        """
        NOTE: `invalidityType` and `invalidityPosition` must match those specified in `InvalidityInfo`.
        """
        
        return SyntaxValidationResult(
            resultType=SyntaxValidationResult.ResultType.INVALID,
            invalidityInfo=SyntaxValidationResult.InvalidityInfo(
                invalidityType=invalidityType,
                invalidityPosition=invalidityPosition
            )
        )
    
    def __eq__(self, __value: Self) -> bool:
        if self.resultType != __value.resultType:
            return False
        
        match self.resultType:
            case SyntaxValidationResult.ResultType.VALID:
                return True
            case SyntaxValidationResult.ResultType.INVALID:
                return self.invalidityInfo == __value.invalidityInfo


# convenient classes
_InvalidityInfo = SyntaxValidationResult.InvalidityInfo
_InvalidityTypes = FilterSyntaxInvalidityType
_InvalidityPosition = SyntaxValidationResult.InvalidityInfo.InvalidityPosition


_is_children_all_valid = lambda children_validation_results: all(child.isValid for child in children_validation_results)
_get_first_invalid_child_result = lambda children_validation_results: next(iter(filter(lambda x: not x.isValid, children_validation_results)))


# convenient methods
def _validation_result_from_children_results(children_validation_results: Iterable[SyntaxValidationResult]):
    if _is_children_all_valid(children_validation_results):
        return SyntaxValidationResult.valid()
    
    return _get_first_invalid_child_result(children_validation_results)


# TODO: add tests for int & float
# TODO: write tests for int / float support
def checkFilterSyntax(element: ET._Element) -> SyntaxValidationResult:
    filterOpAttribName: str = AttributeNames.filterOperationTypeAttribute
    
    # convenient objects
    invalidityPosition = _InvalidityPosition(element.sourceline)

    def hasFilterOpAttribute(element: ET._Element) -> bool:
        return filterOpAttribName in element.keys()
    
    match element.tag:
        case TagNames.DICT:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                
                case FilterOperationTypes.ALL:
                    # all children must be of named-field type
                    children_tags = {child.tag for child in element}
                    
                    if not children_tags.issubset({TagNames.NAMED_FIELD}):
                        # invalid tag for a child of dict
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.DICT_INVALID_CHILD_TAG,
                            invalidityPosition=invalidityPosition
                        )
                    
                    children_validity = [checkFilterSyntax(child) for child in element]
                    
                    if not _is_children_all_valid(children_validity):
                        # at least one child is invalid
                        return _get_first_invalid_child_result(children_validity)
                    
                    # all children must have different names
                    children_names = {child.attrib[AttributeNames.nameAttribute] for child in element}

                    if len(children_names) != len(element):
                        # duplicated names detected
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.DICT_DUPLICATE_KEYS,
                            invalidityPosition=invalidityPosition
                        )
            
                    return SyntaxValidationResult.valid()
                
                case FilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                
                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )

        case TagNames.LIST:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.ALL:
                    children_validity = [checkFilterSyntax(child) for child in element]
                    
                    return _validation_result_from_children_results(children_validity)
                case FilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
        
        case TagNames.TAG_COLLECTION:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.EXPLICIT_TAG_MATCH | FilterOperationTypes.IMPLICIT_TAG_MATCH:
                    # make sure that all children are tagged `tag` and that each child is valid

                    child_tags = {child.tag for child in element}

                    if not child_tags.issubset({TagNames.CONDENSED_TAGS}):
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TAG_COLLECTION_INVALID_CHILD_TAG,
                            invalidityPosition=invalidityPosition
                        )
                    
                    children_validity = [checkFilterSyntax(child) for child in element]
                    
                    return _validation_result_from_children_results(children_validity)
                
                case FilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                
                case _:
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
        
        case TagNames.CONDENSED_TAGS:
            # a `tag` must have no filter operation type attribute
            if hasFilterOpAttribute(element):
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_FILTER_OPERATION_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            # a `tag` must have non-empty text content
            if element.text is None or element.text == '':
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_EMPTY_CONTENT,
                    invalidityPosition=invalidityPosition
                )
                
            # a `tag` must have no children
            if len(element) > 0:
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=invalidityPosition
                )
            
            # the syntax of a tag must be valid
            try:
                parseCondensedTags(element.text)
            except InvalidCondensedTagsException as e:
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.CONDENSED_TAGS_INVALID_SYNTAX,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
                
        case TagNames.NAMED_FIELD:
            if AttributeNames.nameAttribute not in element.keys():
                # named field elements must have a name attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.NAMED_FIELD_MISSING_NAME_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )

            if len(element) != 1:
                # named field elements must have exactly one child
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.NAMED_FIELD_INCORRECT_CHILDREN_COUNT,
                    invalidityPosition=invalidityPosition
                )
            
            return checkFilterSyntax(element[0])

        case TagNames.STRING:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.EQUALS:
                    if len(element) > 0:
                        # string filters can have no children
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()

                case FilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()

                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
        
        case TagNames.BOOL:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.EQUALS:
                    # TODO: check for validity of boolean literal
                    if len(element) > 0:
                        # terminal filters can have no children
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()

                case FilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()

                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
        
        case TagNames.INT:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.EQUALS | \
                        FilterOperationTypes.GREATER_THAN | \
                        FilterOperationTypes.GREATER_THAN_OR_EQUALS | \
                        FilterOperationTypes.LESS_THAN | \
                        FilterOperationTypes.LESS_THAN_OR_EQUALS:
                    if len(element) > 0:
                        # terminal filters can have no children
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
                            invalidityPosition=invalidityPosition
                        )
                        
                    try:
                        number = int(element.text.strip())
                        
                        return SyntaxValidationResult.valid()
                    except Exception:
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.INT_INVALID_INT_LITERAL,
                            invalidityPosition=invalidityPosition
                        )

                case FilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()

                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
        
        case TagNames.FLOAT:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.EQUALS | \
                        FilterOperationTypes.GREATER_THAN | \
                        FilterOperationTypes.GREATER_THAN_OR_EQUALS | \
                        FilterOperationTypes.LESS_THAN | \
                        FilterOperationTypes.LESS_THAN_OR_EQUALS:
                    if len(element) > 0:
                        # terminal filters can have no children
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
                            invalidityPosition=invalidityPosition
                        )
                        
                    try:
                        number = float(element.text.strip())
                        
                        return SyntaxValidationResult.valid()
                    except Exception:
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.FLOAT_INVALID_FLOAT_LITERAL,
                            invalidityPosition=invalidityPosition
                        )

                case FilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()

                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )

        case TagNames.TYPE_DECLARATION:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.TYPE_MATCH:
                    if len(element) != 1:
                        # type declaration elements must have exactly one child
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_INCORRECT_CHILD_COUNT,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return checkFilterSyntax(element[0])
                
                case FilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                
                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
        
        case TagNames.LOGICAL:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.AND | FilterOperationTypes.OR:
                    if len(element) <= 1:
                        # AND / OR operations must have at least two children
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.LOGICAL_INCORRECT_CHILD_COUNT,
                            invalidityPosition=invalidityPosition
                        )
                    
                    children_validity = [checkFilterSyntax(child) for child in element]
                    
                    return _validation_result_from_children_results(children_validity)
                
                case FilterOperationTypes.NOT:
                    if len(element) != 1:
                        # NOT operation must have exactly one child
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.LOGICAL_INCORRECT_CHILD_COUNT,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return checkFilterSyntax(element[0])
                
                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )

        case TypeDeclarationTagNames.STRING | \
                TypeDeclarationTagNames.BOOL | \
                TypeDeclarationTagNames.INT | \
                TypeDeclarationTagNames.FLOAT:
            if len(element) > 0 or element.text is not None:
                # primitive, atomic types declarations can have no children or enclosed content
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
            
        case TypeDeclarationTagNames.TENSOR:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    children_tags = {child.tag for child in element}

                    if not children_tags.issubset({TypeDeclarationTagNames.DIM, TagNames.LOGICAL}):
                        # invalid tag (s) found on children
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_TENSOR_INVALID_CHILD_TAG,
                            invalidityPosition=invalidityPosition
                        )
                    
                    children_validity = [checkFilterSyntax(child) for child in element]
                    
                    return _validation_result_from_children_results(children_validity)

                case TypeDeclarationFilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                
                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
            
        case TypeDeclarationTagNames.LIST:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    if len(element) != 1:
                        # list type declaration must have exactly one child if filter operation type is not none
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_LIST_INCORRECT_CHILD_COUNT,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return checkFilterSyntax(element[0])
                case TypeDeclarationFilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
            
        case TypeDeclarationTagNames.TUPLE:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    children_validity = [checkFilterSyntax(child) for child in element]
                    
                    return _validation_result_from_children_results(children_validity)
                
                case TypeDeclarationFilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                
                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
            
        case TypeDeclarationTagNames.NAMED_VALUE_COLLECTION:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )

            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL:
                    # all children must be named values
                    children_tags = {child.tag for child in element}

                    if not children_tags.issubset({TypeDeclarationTagNames.NAMED_VALUE}):
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_INVALID_CHILD_TAG,
                            invalidityPosition=invalidityPosition
                        )
                    
                    children_validity = [checkFilterSyntax(child) for child in element]
                    
                    if not _is_children_all_valid(children_validity):
                        # at least one of the children is invalid
                        return _get_first_invalid_child_result(children_validity)
                    
                    # all children must have different names
                    children_names = {child.attrib[TypeDeclarationAttributeNames.namedValueNameAttributeName]
                                      for child in element}
                    
                    if len(children_names) != len(element):
                        # duplicate names detected
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                
                case TypeDeclarationFilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                
                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
            
        case TypeDeclarationTagNames.NAMED_VALUE:
            if TypeDeclarationAttributeNames.namedValueNameAttributeName not in element.keys():
                # must have a name attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_MISSING_NAME_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            if len(element) != 1:
                # must have exactly one child
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_INCORRECT_CHILDREN_COUNT,
                    invalidityPosition=invalidityPosition
                )
            
            return checkFilterSyntax(element[0])
            
        case TypeDeclarationTagNames.DIM:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            if len(element) > 0:
                # dim filters can have no children
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_DIM_ILLEGAL_CHILD,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.EQUALS | \
                        TypeDeclarationFilterOperationTypes.LESS_THAN | \
                        TypeDeclarationFilterOperationTypes.LESS_THAN_OR_EQUALS | \
                        TypeDeclarationFilterOperationTypes.GREATER_THAN | \
                        TypeDeclarationFilterOperationTypes.GREATER_THAN_OR_EQUALS:
                    
                    try:
                        dim = int(element.text)
                    except Exception:
                        # if the filter operation type is a comparison, enclosed text must be able to be parsed into an integer
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                case TypeDeclarationFilterOperationTypes.NONE:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.ILLEGAL_CONTENT_ON_FILTER_OPERATION_TYPE_NONE,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                case _:
                    # invalid filter operation type
                    return SyntaxValidationResult.invalid(
                        invalidityType=_InvalidityTypes.INVALID_FILTER_OPERATION_TYPE,
                        invalidityPosition=invalidityPosition
                    )
                
        case _:
            # invalid tag
            return SyntaxValidationResult.invalid(
                invalidityType=_InvalidityTypes.INVALID_TAG,
                invalidityPosition=invalidityPosition
            )


@dataclass
class FilterValidationResult:
    
    class ResultType:
        VALID = auto()
        INVALID = auto()

    @dataclass
    class InvalidityInfo:
        
        class InvalidityType(Enum):
            INVALID_SYNTAX = auto()
            UNKNOWN_TAGS = auto()
    
        invalidityType: InvalidityType
        invalidityInfo: Union[SyntaxValidationResult.InvalidityInfo, Set[str]]
        
        def __eq__(self, other: Self) -> bool:
            return self.invalidityType == other.invalidityType and self.invalidityInfo == other.invalidityInfo
    
    resultType: ResultType
    invalidityInfo: InvalidityInfo | None
    
    @property
    def isValid(self) -> bool:
        return self.resultType == FilterValidationResult.resultType.VALID
    
    def __eq__(self, other: Self) -> bool:
        return self.resultType == other.resultType and self.invalidityInfo == other.invalidityInfo
    
    @staticmethod
    def valid() -> Self:
        return FilterValidationResult(
            resultType=FilterValidationResult.ResultType.VALID,
            invalidityInfo=None
        )
    
    @staticmethod
    def invalid(invalidityType, invalidityInfo) -> Self:
        """NOTE:
        
        `invalidityType` and `invalidityInfo` must match the types specified in `InvalidityInfo`.
        """

        return FilterValidationResult(
            resultType=FilterValidationResult.ResultType.INVALID,
            invalidityInfo=FilterValidationResult.InvalidityInfo(
                invalidityType=invalidityType,
                invalidityInfo=invalidityInfo
            )
        )
    
        
def validateFilter(filterElement: ET._Element, tagName: str | None=None, loadedTags: Dict[str, ET._Element] | None=None) -> FilterValidationResult:
    """Checks that a filter element is valid.
    This function can check the validity of both regular filters and tags.
    
    For an ordinary filter that is not a tag, pass `tagName` as `None`.
    For a tag, pass the name of the tag in `tagName`.

    Args:
        filterElement (ET._Element): The filter to check.
        tagName (str | None, optional): The name of the tag (if applicable). Defaults to None.
        loadedTags (Dict[str, ET._Element] | None, optional): Loaded tags. Defaults to None.

    Returns:
        FilterValidationResult: The result of the validation.
    """
    if loadedTags is None:
        loadedTags = loadTags()
    
    # check syntax
    syntax_check_result = checkFilterSyntax(filterElement)
    
    if not syntax_check_result.isValid:
        return FilterValidationResult.invalid(
            invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX,
            invalidityInfo=syntax_check_result.invalidityInfo
        )
    
    # check tags
    def find_unmatched_tags_for_tag_collection(tag_collection: ET._Element) -> Set[str]:
        tags = set().union(*[parseCondensedTags(child.text) for child in tag_collection])
        undefined_tags = tags.difference(loadedTags.keys())

        # if this is an explicit match, referencing self is allowed;
        # if this is an implicit match, referencing self is not allowed, as that would result in an infinite recursion
        return undefined_tags.difference({tagName}) \
                if (tagName is not None and 
                    tag_collection.attrib[AttributeNames.filterOperationTypeAttribute] == FilterOperationTypes.EXPLICIT_TAG_MATCH) \
            else undefined_tags
        
        
    tag_collections = filterElement.findall(r'.//' + TagNames.TAG_COLLECTION)
    unknown_tags = set().union(*[find_unmatched_tags_for_tag_collection(tag_collection) for tag_collection in tag_collections])
    
    if len(unknown_tags) > 0:
        return FilterValidationResult.invalid(
            invalidityType=FilterValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS,
            invalidityInfo=unknown_tags
        )
    
    return FilterValidationResult.valid()
