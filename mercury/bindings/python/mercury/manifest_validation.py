from dataclasses import dataclass
from enum import Enum, auto
from typing import Self, Iterable

from lxml import etree as ET

import sys
import os

from .interface import (
    TagNames, AttributeNames, FilterOperationTypes, filterXMLfromArgs,
    TypeDeclarationTagNames, TypeDeclarationFilterOperationTypes, TypeDeclarationAttributeNames, ManifestSyntaxInvalidityType
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
        
        invalidityType: ManifestSyntaxInvalidityType
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
_InvalidityTypes = ManifestSyntaxInvalidityType
_InvalidityPosition = SyntaxValidationResult.InvalidityInfo.InvalidityPosition


_get_first_invalid_child_result = lambda children_validation_results: next(iter(filter(lambda x: not x.isValid, children_validation_results)))


# convenient methods
def _validation_result_from_children_results(children_validation_results: Iterable[SyntaxValidationResult]):
    if all(result.isValid for result in children_validation_results):
        return SyntaxValidationResult.valid()
    
    return _get_first_invalid_child_result(children_validation_results)


def checkSyntax(element: ET._Element) -> SyntaxValidationResult:
    # convenient objects
    invalidityPosition = _InvalidityPosition(element.sourceline)

    match element.tag:
        case TagNames.DICT.value:
            # all children must be of named-field type
            children_tags = {child.tag for child in element}
            if children_tags != {TagNames.NAMED_FIELD.value}:
                # invalid tag for a child of dict
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.DICT_INVALID_CHILD_TAG,
                    invalidityPosition=invalidityPosition
                )
            
            children_validity = [checkSyntax(child) for child in element]
            
            if not all(child.isValid for child in children_validity):
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
        
        case TagNames.LIST.value:
            children_validity = [checkSyntax(child) for child in element]
            return _validation_result_from_children_results(children_validity)

        case TagNames.NAMED_FIELD.value:
            # element must have a "name" attribute
            if AttributeNames.nameAttribute.value not in element.attrib.keys():
                # element does not have a "name" attribute
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.NAMED_FIELD_MISSING_NAME_ATTRIBUTE,
                    invalidityPosition=invalidityPosition
                )

            # length of children must be 1
            if len(element) != 1:
                # length of children is not 1
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.NAMED_FIELD_INCORRECT_CHILDREN_COUNT,
                    invalidityPosition=invalidityPosition
                )
            
            return checkSyntax(element[0])

        case TagNames.STRING.value:
            if len(element) > 0:
                # child element is detected on a string element
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
        case TagNames.BOOL.value:
            if len(element) > 0:
                # child element is detected on a bool element
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
                    invalidityPosition=invalidityPosition
                )
            
            # TODO: check validity of bool literal
            
            return SyntaxValidationResult.valid()
        
        case TagNames.INT.value:
            if len(element) > 0:
                # child element is detected on a terminal element
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
                    invalidityPosition=invalidityPosition
                )
            
            try:
                number = int(element.text.strip())

                return SyntaxValidationResult.valid()
            except Exception:
                return  SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.INT_INVALID_INT_LITERAL,
                    invalidityPosition=invalidityPosition
                )
        
        case TagNames.FLOAT.value:
            if len(element) > 0:
                # child element is detected on a terminal element
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
                    invalidityPosition=invalidityPosition
                )
            
            try:
                number = float(element.text.strip())

                return SyntaxValidationResult.valid()
            except Exception:
                return  SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.FLOAT_INVALID_FLOAT_LITERAL,
                    invalidityPosition=invalidityPosition
                )

        case TagNames.TYPE_DECLARATION.value:
            if len(element) != 1:
                # type declaration elements must have exactly one child
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_INCORRECT_CHILD_COUNT,
                    invalidityPosition=invalidityPosition
                )

            return checkTypeDeclarationSyntax(element[0])

        case _:
            # invalid tag name
            return SyntaxValidationResult.invalid(
                invalidityType=_InvalidityTypes.INVALID_TAG,
                invalidityPosition=invalidityPosition
            )


def checkTypeDeclarationSyntax(element: ET._Element) -> SyntaxValidationResult:
    # convenient objects
    invalidityPosition = _InvalidityPosition(element.sourceline)

    match element.tag:
        case TypeDeclarationTagNames.STRING.value | \
                TypeDeclarationTagNames.BOOL.value | \
                TypeDeclarationTagNames.INT.value | \
                TypeDeclarationTagNames.FLOAT.value:
            if len(element) > 0 or element.text is not None:
                # a terminal type declaration must have no children or enclosed content
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
        case TypeDeclarationTagNames.TENSOR.value:
            # all children must be of dim type
            children_tags = {child.tag for child in element}

            if children_tags != {TypeDeclarationTagNames.DIM.value}:
                # child tag is not dim
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_TENSOR_INVALID_CHILD_TAG,
                    invalidityPosition=invalidityPosition
                )
                
            children_validity = [checkTypeDeclarationSyntax(child) for child in element]
            
            return _validation_result_from_children_results(children_validity)
        
        case TypeDeclarationTagNames.LIST.value:
            if len(element) != 1:
                # a list type declaration must have exactly one child
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_LIST_INCORRECT_CHILD_COUNT,
                    invalidityPosition=invalidityPosition
                )
            
            return checkTypeDeclarationSyntax(element[0])
        
        case TypeDeclarationTagNames.TUPLE.value:
            children_validity = [checkTypeDeclarationSyntax(child) for child in element]
            
            return _validation_result_from_children_results(children_validity)
        
        case TypeDeclarationTagNames.NAMED_VALUE_COLLECTION.value:
            # all children must be of named-value type
            children_tags = {child.tag for child in element}
            
            if children_tags != {TypeDeclarationTagNames.NAMED_VALUE.value}:
                # invalid tag for a child of dict
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_INVALID_CHILD_TAG,
                    invalidityPosition=invalidityPosition
                )
            
            children_validity = [checkTypeDeclarationSyntax(child) for child in element]
            
            if not all(child.isValid for child in children_validity):
                # at least one child is invalid
                return _get_first_invalid_child_result(children_validity)
            
            # all children must have different names
            children_names = {child.attrib[TypeDeclarationAttributeNames.namedValueNameAttributeName.value] for child in element}

            if len(children_names) != len(element):
                # duplicated names detected
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
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
            
            return checkTypeDeclarationSyntax(element[0])
        
        case TypeDeclarationTagNames.DIM.value:
            if len(element) > 0:
                # dim elements can have no children
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_DIM_ILLEGAL_CHILD,
                    invalidityPosition=invalidityPosition
                )
            
            try:
                dim = int(element.text)
            except Exception:
                # dim element must be able to be parsed into an integer
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
        case _:
            # invalid tag name
            return SyntaxValidationResult.invalid(
                invalidityType=_InvalidityTypes.INVALID_TAG,
                invalidityPosition=invalidityPosition
            )

