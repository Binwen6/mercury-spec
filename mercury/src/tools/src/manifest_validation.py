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


def checkSyntax(element: ET._Element) -> bool:
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
            
            if not all(children_validity):
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


def checkTypeDeclarationSyntax(element: ET._Element) -> bool:
    # convenient objects
    invalidityPosition = _InvalidityPosition(element.sourceline)

    match element.tag:
        case TypeDeclarationTagNames.STRING.value:
            if len(element) > 0 or element.text is not None:
                # a string / bool type declaration must have no children or enclosed content
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.STRING_ILLEGAL_CHILD,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
        case TypeDeclarationTagNames.BOOL.value:
            if len(element) > 0 or element.text is not None:
                # a string / bool type declaration must have no children or enclosed content
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.BOOL_ILLEGAL_CHILD,
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
            
            return _validation_result_from_children_results(checkTypeDeclarationSyntax(child) for child in element)
        
        case TypeDeclarationTagNames.LIST.value:
            if len(element) != 1:
                # a list type declaration must have exactly one child
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_LIST_INCORRECT_CHILDREN_COUNT,
                    invalidityPosition=invalidityPosition
                )
            
            return checkTypeDeclarationSyntax(element[0])
        
        case TypeDeclarationTagNames.TUPLE.value:
            return _validation_result_from_children_results(checkTypeDeclarationSyntax(child) for child in element)
        
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
            
            if not all(children_validity):
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
            
            return checkTypeDeclarationFilterSyntax(element[0])
        
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


# TODO: write tests
def checkFilterSyntax(element: ET._Element) -> bool:
    filterOpAttribName: str = AttributeNames.filterOperationTypeAttribute.value

    def hasFilterOpAttribute(element: ET._Element) -> bool:
        return filterOpAttribName in element.keys()
    
    match element.tag:
        case TagNames.dictType.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return False
            
            match element.attrib[filterOpAttribName]:
                
                case FilterOperationTypes.ALL.value:
                    # all children must be of named-field type
                    children_tags = {child.tag for child in element}
                    
                    if children_tags != {TagNames.namedField.value}:
                        # invalid tag for a child of dict
                        return False
                    
                    children_validity = [checkFilterSyntax(child) for child in element]
                    
                    if not all(children_validity):
                        # at least one child is invalid
                        return False
                    
                    # all children must have different names
                    children_names = {child.attrib[AttributeNames.nameAttribute.value] for child in element}

                    if len(children_names) != len(element):
                        # duplicated names detected
                        return False
            
                    return SyntaxValidationResult.valid()
                
                case FilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return SyntaxValidationResult.valid()
                
                case _:
                    # invalid filter operation type
                    return False

        case TagNames.listType.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return False
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.ALL.value:
                    return all(checkFilterSyntax(child) for child in element)
                case FilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return SyntaxValidationResult.valid()
                case _:
                    # invalid filter operation type
                    return False
                
        case TagNames.namedField.value:
            if AttributeNames.nameAttribute.value not in element.keys():
                # named field elements must have a name attribute
                return False

            if len(element) != 1:
                # named field elements must have exactly one child
                return False
            
            return checkFilterSyntax(element[0])

        case TagNames.string.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return False
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.EQUALS.value:
                    if len(element) > 0:
                        # string filters can have no children
                        return False
                    
                    return SyntaxValidationResult.valid()

                case FilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return SyntaxValidationResult.valid()

                case _:
                    # invalid filter operation type
                    return False

        case TagNames.typeDeclaration.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return False
            
            match element.attrib[filterOpAttribName]:
                case FilterOperationTypes.TYPE_MATCH.value:
                    if len(element) != 1:
                        # type declaration elements must have exactly one child
                        return False
                    
                    return checkTypeDeclarationFilterSyntax(element[0])
                
                case FilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return SyntaxValidationResult.valid()
                
                case _:
                    # invalid filter operation type
                    return False
        
        case _:
            # invalid tag
            return False


# TODO: write tests
def checkTypeDeclarationFilterSyntax(element: ET._Element) -> bool:
    filterOpAttribName: str = AttributeNames.filterOperationTypeAttribute.value

    def hasFilterOpAttribute(element: ET._Element) -> bool:
        return filterOpAttribName in element.keys()
    
    match element.tag:
        case TypeDeclarationTagNames.STRING.value | TypeDeclarationTagNames.BOOL.value:
            if len(element) > 0 or element.text is not None:
                # primitive, atomic types declarations can have no children or enclosed content
                return False
            
            return SyntaxValidationResult.valid()
            
        case TypeDeclarationTagNames.TENSOR.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return False
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    children_tags = {child.tag for child in element}

                    if children_tags != {TypeDeclarationTagNames.DIM.value}:
                        # invalid tag (s) found on children
                        return False
                    
                    return all(checkTypeDeclarationFilterSyntax(child) for child in element)

                case TypeDeclarationFilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return SyntaxValidationResult.valid()
                
                case _:
                    # invalid filter operation type
                    return False
            
        case TypeDeclarationTagNames.LIST.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return False
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    if len(element) != 1:
                        # list type declaration must have one child only if filter operation type is not none
                        return False
                    
                    return checkTypeDeclarationFilterSyntax(element[0])
                case TypeDeclarationFilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return SyntaxValidationResult.valid()
                case _:
                    # invalid filter operation type
                    return False
            
        case TypeDeclarationTagNames.TUPLE.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return False
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    return all(checkTypeDeclarationFilterSyntax(child) for child in element)
                case TypeDeclarationFilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return SyntaxValidationResult.valid()
                case _:
                    # invalid filter operation type
                    return False
            
        case TypeDeclarationTagNames.NAMED_VALUE_COLLECTION.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return False

            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.ALL.value:
                    # all children must be named values
                    children_tags = {child.tag for child in element}

                    if children_tags != {TypeDeclarationTagNames.NAMED_VALUE.value}:
                        return False
                    
                    if not all(checkTypeDeclarationFilterSyntax(child) for child in element):
                        # at least one of the children is invalid
                        return False
                    
                    # all children must have different names
                    children_names = {child.attrib[TypeDeclarationAttributeNames.namedValueNameAttributeName.value]
                                      for child in element}
                    
                    if len(children_names) != len(element):
                        # duplicate names detected
                        return False
                    
                    return SyntaxValidationResult.valid()
                
                case TypeDeclarationFilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return SyntaxValidationResult.valid()
                
                case _:
                    # invalid filter operation type
                    return False
            
        case TypeDeclarationTagNames.NAMED_VALUE.value:
            if TypeDeclarationAttributeNames.namedValueNameAttributeName.value not in element.keys():
                # must have a name attribute
                return False
            
            if len(element) != 1:
                # must have exactly one child
                return False
            
            return checkTypeDeclarationFilterSyntax(element[0])
            
        case TypeDeclarationTagNames.DIM.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return False
            
            if len(element) > 0:
                # dim filters can have no children
                return False
            
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
                        return False
                    
                    return SyntaxValidationResult.valid()
                case TypeDeclarationFilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text is not None:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return SyntaxValidationResult.valid()
                case _:
                    # invalid filter operation type
                    return False
                
        case _:
            # invalid tag
            return False


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
