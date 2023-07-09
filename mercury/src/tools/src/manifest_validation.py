from dataclasses import dataclass
from enum import Enum, auto
from typing import Self, Iterable

from lxml import etree as ET

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'spec-language-interfaces'))

from python_interface.interface import (
    TagNames, AttributeNames, FilterOperationTypes, filterXMLfromArgs,
    TypeDeclarationTagNames, TypeDeclarationFilterOperationTypes, TypeDeclarationAttributeNames
)


@dataclass
class SyntaxValidationResult:
    
    class ResultType(Enum):
        VALID = auto()
        INVALID = auto()
        
    @dataclass
    class InvalidityInfo:
        
        class InvalidityType(Enum):
            INVALID_TAG = auto()

            DICT_INVALID_CHILD_TAG = auto()
            DICT_DUPLICATE_KEYS = auto()
            
            NAMED_FIELD_MISSING_NAME_ATTRIBUTE = auto()
            NAMED_FIELD_INCORRECT_CHILDREN_COUNT = auto()
            
            # a string element cannot have any children
            STRING_ILLEGAL_CHILD = auto()
            
            # a bool element cannot have any children
            BOOL_ILLEGAL_CHILD = auto()
            
            TYPE_DECLARATION_INCORRECT_CHILDREN_COUNT = auto()
            
            TYPE_DECLARATION_BOOL_INVALID_CHILD = auto()

            TYPE_DECLARATION_STRING_INVALID_CHILD = auto()
            
            TYPE_DECLARATION_TENSOR_INVALID_CHILD_TAG = auto()

            TYPE_DECLARATION_LIST_INCORRECT_CHILDREN_COUNT = auto()

            TYPE_DECLARATION_NAMED_VALUE_COLLECTION_INVALID_CHILD_TAG = auto()
            TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS = auto()
            
            TYPE_DECLARATION_NAMED_VALUE_MISSING_NAME_ATTRIBUTE = auto()
            TYPE_DECLARATION_NAMED_VALUE_INCORRECT_CHILDREN_COUNT = auto()
            
            TYPE_DECLARATION_DIM_ILLEGAL_CHILD = auto()
            TYPE_DECLARATION_DIM_ILLEGAL_INTEGER_LITERAL = auto()
            
        @dataclass
        class InvalidityPosition:
            line: int

            def __eq__(self, __value: Self) -> bool:
                return self.line == __value.line
        
        invalidityType: InvalidityType
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
_InvalidityTypes = SyntaxValidationResult.InvalidityInfo.InvalidityType
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
        case TagNames.dictType.value:
            # all children must be of named-field type
            children_tags = {child.tag for child in element}
            if children_tags != {TagNames.namedField.value}:
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
        
        case TagNames.listType.value:
            children_validity = [checkSyntax(child) for child in element]
            return _validation_result_from_children_results(children_validity)

        case TagNames.namedField.value:
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
            
            return SyntaxValidationResult.valid()

        case TagNames.string.value:
            if len(element) > 0:
                # child element is detected on a string element
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.STRING_ILLEGAL_CHILD,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()

        case TagNames.typeDeclaration.value:
            if len(element) != 1:
                # type declaration elements must have exactly one child
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_INCORRECT_CHILDREN_COUNT,
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
        case TypeDeclarationTagNames.STRING.value:
            if len(element) > 0 or element.text is not None:
                # a string / bool type declaration must have no children or enclosed content
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_STRING_INVALID_CHILD,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
        case TypeDeclarationTagNames.BOOL.value:
            if len(element) > 0 or element.text is not None:
                # a string / bool type declaration must have no children or enclosed content
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_BOOL_INVALID_CHILD,
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
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_LIST_INCORRECT_CHILDREN_COUNT,
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

