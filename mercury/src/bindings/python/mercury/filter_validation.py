from dataclasses import dataclass
from enum import Enum, auto
from typing import Self, Iterable

from lxml import etree as ET

import sys
import os

from .interface import (
    TagNames, AttributeNames, FilterOperationTypes, filterXMLfromArgs,
    TypeDeclarationTagNames, TypeDeclarationFilterOperationTypes, TypeDeclarationAttributeNames,
    FilterSyntaxInvalidityType
)


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


def checkFilterSyntax(element: ET._Element) -> SyntaxValidationResult:
    filterOpAttribName: str = AttributeNames.filterOperationTypeAttribute.value
    
    # convenient objects
    invalidityPosition = _InvalidityPosition(element.sourceline)

    def hasFilterOpAttribute(element: ET._Element) -> bool:
        return filterOpAttribName in element.keys()
    
    match element.tag:
        case TagNames.dictType.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                
                case FilterOperationTypes.ALL.value:
                    # all children must be of named-field type
                    children_tags = {child.tag for child in element}
                    
                    if children_tags != {TagNames.namedField.value}:
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
                    children_names = {child.attrib[AttributeNames.nameAttribute.value] for child in element}

                    if len(children_names) != len(element):
                        # duplicated names detected
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.DICT_DUPLICATE_KEYS,
                            invalidityPosition=invalidityPosition
                        )
            
                    return SyntaxValidationResult.valid()
                
                case FilterOperationTypes.NONE.value:
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

        case TagNames.listType.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.ALL.value:
                    children_validity = [checkFilterSyntax(child) for child in element]
                    
                    return _validation_result_from_children_results(children_validity)
                case FilterOperationTypes.NONE.value:
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
                
        case TagNames.namedField.value:
            if AttributeNames.nameAttribute.value not in element.keys():
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

        case TagNames.string.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.EQUALS.value:
                    if len(element) > 0:
                        # string filters can have no children
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.STRING_ILLEGAL_CHILD,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()

                case FilterOperationTypes.NONE.value:
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

        case TagNames.typeDeclaration.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.TYPE_MATCH.value:
                    if len(element) != 1:
                        # type declaration elements must have exactly one child
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_INCORRECT_CHILD_COUNT,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return checkTypeDeclarationFilterSyntax(element[0])
                
                case FilterOperationTypes.NONE.value:
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


def checkTypeDeclarationFilterSyntax(element: ET._Element) -> SyntaxValidationResult:
    filterOpAttribName: str = AttributeNames.filterOperationTypeAttribute.value

    # convenient objects
    invalidityPosition = _InvalidityPosition(element.sourceline)

    def hasFilterOpAttribute(element: ET._Element) -> bool:
        return filterOpAttribName in element.keys()
    
    match element.tag:
        case TypeDeclarationTagNames.STRING.value:
            if len(element) > 0 or element.text is not None:
                # primitive, atomic types declarations can have no children or enclosed content
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_STRING_ILLEGAL_CONTENT,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
        case TypeDeclarationTagNames.BOOL.value:
            if len(element) > 0 or element.text is not None:
                # primitive, atomic types declarations can have no children or enclosed content
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_BOOL_ILLEGAL_CONTENT,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
            
        case TypeDeclarationTagNames.TENSOR.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    children_tags = {child.tag for child in element}

                    if children_tags != {TypeDeclarationTagNames.DIM.value}:
                        # invalid tag (s) found on children
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_TENSOR_INVALID_CHILD_TAG,
                            invalidityPosition=invalidityPosition
                        )
                    
                    children_validity = [checkTypeDeclarationFilterSyntax(child) for child in element]
                    
                    return _validation_result_from_children_results(children_validity)

                case TypeDeclarationFilterOperationTypes.NONE.value:
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
            
        case TypeDeclarationTagNames.LIST.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    if len(element) != 1:
                        # list type declaration must have exactly one child if filter operation type is not none
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_LIST_INCORRECT_CHILD_COUNT,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return checkTypeDeclarationFilterSyntax(element[0])
                case TypeDeclarationFilterOperationTypes.NONE.value:
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
            
        case TypeDeclarationTagNames.TUPLE.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    children_validity = [checkTypeDeclarationFilterSyntax(child) for child in element]
                    
                    return _validation_result_from_children_results(children_validity)
                
                case TypeDeclarationFilterOperationTypes.NONE.value:
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
            
        case TypeDeclarationTagNames.NAMED_VALUE_COLLECTION.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.MISSING_FILTER_OPERATION_TYPE_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )

            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    # all children must be named values
                    children_tags = {child.tag for child in element}

                    if children_tags != {TypeDeclarationTagNames.NAMED_VALUE.value}:
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_INVALID_CHILD_TAG,
                            invalidityPosition=invalidityPosition
                        )
                    
                    children_validity = [checkTypeDeclarationFilterSyntax(child) for child in element]
                    
                    if not _is_children_all_valid(children_validity):
                        # at least one of the children is invalid
                        return _get_first_invalid_child_result(children_validity)
                    
                    # all children must have different names
                    children_names = {child.attrib[TypeDeclarationAttributeNames.namedValueNameAttributeName.value]
                                      for child in element}
                    
                    if len(children_names) != len(element):
                        # duplicate names detected
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                
                case TypeDeclarationFilterOperationTypes.NONE.value:
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
            
        case TypeDeclarationTagNames.NAMED_VALUE.value:
            if TypeDeclarationAttributeNames.namedValueNameAttributeName.value not in element.keys():
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
            
            return checkTypeDeclarationFilterSyntax(element[0])
            
        case TypeDeclarationTagNames.DIM.value:
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
                case TypeDeclarationFilterOperationTypes.EQUALS.value | \
                        TypeDeclarationFilterOperationTypes.LESS_THAN.value | \
                        TypeDeclarationFilterOperationTypes.LESS_THAN_OR_EQUALS.value | \
                        TypeDeclarationFilterOperationTypes.GREATER_THAN.value | \
                        TypeDeclarationFilterOperationTypes.GREATER_THAN_OR_EQUALS.value:
                    
                    try:
                        dim = int(element.text)
                    except Exception:
                        # if the filter operation type is a comparison, enclosed text must be able to be parsed into an integer
                        return SyntaxValidationResult.invalid(
                            invalidityType=_InvalidityTypes.TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL,
                            invalidityPosition=invalidityPosition
                        )
                    
                    return SyntaxValidationResult.valid()
                case TypeDeclarationFilterOperationTypes.NONE.value:
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


def validateManifest(manifest: ET._Element):
    """Validates manifest data, throwing an error if the manifest is invalid.

    Args:
        manifest (ET._Element): The manifest data to validated, in parsed XML form.
    """
    
    # syntax check
    

def validateFilter(filterElement: ET._Element):
    """Validates a filter in XML form, throwing an error if the filter is invalid.

    Args:
        filterElement (ET._Element): The filter to validate.
    """