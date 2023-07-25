from dataclasses import dataclass
from enum import Enum, auto
from typing import Self, Iterable, Union, Dict, List, Set, Tuple

from lxml import etree as ET

import sys
import os

from .specification.interface import (
    TagNames, AttributeNames, FilterOperationTypes, filterXMLfromArgs,
    TypeDeclarationTagNames, TypeDeclarationFilterOperationTypes, TypeDeclarationAttributeNames, ManifestSyntaxInvalidityType,
    ManifestUtils
)
from .specification.load_tags import loadTags
from .config import Config
from .filtering import Filter, matchFilter, FilterMatchResult
from .tag_matching import parseCondensedTags, InvalidCondensedTagsException


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
        case TagNames.DICT:
            # all children must be of named-field type
            children_tags = {child.tag for child in element}
            if not children_tags.issubset({TagNames.NAMED_FIELD}):
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
            children_names = {child.attrib[AttributeNames.nameAttribute] for child in element}

            if len(children_names) != len(element):
                # duplicated names detected
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.DICT_DUPLICATE_KEYS,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
        case TagNames.LIST:
            children_validity = [checkSyntax(child) for child in element]
            return _validation_result_from_children_results(children_validity)

        case TagNames.NAMED_FIELD:
            # element must have a "name" attribute
            if AttributeNames.nameAttribute not in element.attrib.keys():
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

        case TagNames.STRING:
            if len(element) > 0:
                # child element is detected on a string element
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
        case TagNames.BOOL:
            if len(element) > 0:
                # child element is detected on a bool element
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.ILLEGAL_CHILD_ON_TERMINAL_ELEMENT,
                    invalidityPosition=invalidityPosition
                )
            
            # TODO: check validity of bool literal
            
            return SyntaxValidationResult.valid()
        
        case TagNames.INT:
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
        
        case TagNames.FLOAT:
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

        case TagNames.TYPE_DECLARATION:
            if len(element) != 1:
                # type declaration elements must have exactly one child
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_INCORRECT_CHILD_COUNT,
                    invalidityPosition=invalidityPosition
                )

            return checkTypeDeclarationSyntax(element[0])
        
        case TagNames.TAG_COLLECTION:
            children_tags = {child.tag for child in element}

            if not children_tags.issubset({TagNames.CONDENSED_TAGS}):
                # invalid child tag
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TAG_COLLECTION_INVALID_CHILD_TAG,
                    invalidityPosition=invalidityPosition
                )
            
            children_validity = [checkSyntax(child) for child in element]
            
            return _validation_result_from_children_results(children_validity)

        case TagNames.CONDENSED_TAGS:
            if len(element) > 0:
                # illegal child
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_CHILD,
                    invalidityPosition=invalidityPosition
                )
            
            if element.text is None or element.text == '':
                # illegal empty content
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.CONDENSED_TAGS_ILLEGAL_EMPTY_CONTENT,
                    invalidityPosition=invalidityPosition
                )
            
            try:
                parseCondensedTags(element.text)
            except InvalidCondensedTagsException as e:
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.CONDENSED_TAGS_INVALID_SYNTAX,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()

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
        case TypeDeclarationTagNames.STRING | \
                TypeDeclarationTagNames.BOOL | \
                TypeDeclarationTagNames.INT | \
                TypeDeclarationTagNames.FLOAT:
            if len(element) > 0 or element.text is not None:
                # a terminal type declaration must have no children or enclosed content
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_ILLEGAL_CONTENT_ON_TERMINAL_ELEMENT,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
        case TypeDeclarationTagNames.TENSOR:
            # all children must be of dim type
            children_tags = {child.tag for child in element}

            if children_tags != {TypeDeclarationTagNames.DIM}:
                # child tag is not dim
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_TENSOR_INVALID_CHILD_TAG,
                    invalidityPosition=invalidityPosition
                )
                
            children_validity = [checkTypeDeclarationSyntax(child) for child in element]
            
            return _validation_result_from_children_results(children_validity)
        
        case TypeDeclarationTagNames.LIST:
            if len(element) != 1:
                # a list type declaration must have exactly one child
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_LIST_INCORRECT_CHILD_COUNT,
                    invalidityPosition=invalidityPosition
                )
            
            return checkTypeDeclarationSyntax(element[0])
        
        case TypeDeclarationTagNames.TUPLE:
            children_validity = [checkTypeDeclarationSyntax(child) for child in element]
            
            return _validation_result_from_children_results(children_validity)
        
        case TypeDeclarationTagNames.NAMED_VALUE_COLLECTION:
            # all children must be of named-value type
            children_tags = {child.tag for child in element}
            
            if not children_tags.issubset({TypeDeclarationTagNames.NAMED_VALUE}):
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
            children_names = {child.attrib[TypeDeclarationAttributeNames.namedValueNameAttributeName] for child in element}

            if len(children_names) != len(element):
                # duplicated names detected
                return SyntaxValidationResult.invalid(
                    invalidityType=_InvalidityTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DUPLICATE_KEYS,
                    invalidityPosition=invalidityPosition
                )
            
            return SyntaxValidationResult.valid()
        
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
            
            return checkTypeDeclarationSyntax(element[0])
        
        case TypeDeclarationTagNames.DIM:
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


@dataclass
class ManifestValidationResult:
    
    class ResultType(Enum):
        VALID = auto()
        INVALID = auto()
    
    @dataclass
    class InvalidityInfo():
        
        class InvalidityType(Enum):
            INVALID_SYNTAX = auto()
            FAILED_BASE_MODEL_FILTER_MATCH = auto()
            UNKNOWN_TAGS = auto()
            UNMATCHED_TAG = auto()
        
        invalidityType: InvalidityType
        info: Union[SyntaxValidationResult.InvalidityInfo, FilterMatchResult.FailureInfo, Set[str], Tuple[str, FilterMatchResult.FailureInfo]] | None
        
        def __eq__(self, other: Self) -> bool:
            return self.invalidityType == other.invalidityType and self.info == other.info
    
    resultType: ResultType
    invalidityInfo: InvalidityInfo | None
    
    @property
    def isValid(self) -> bool:
        return self.resultType == ManifestValidationResult.ResultType.VALID
    
    def __eq__(self, __value: Self) -> bool:
        return self.resultType == __value.resultType and self.invalidityInfo == __value.invalidityInfo
    
    @staticmethod
    def valid() -> Self:
        return ManifestValidationResult(
            resultType=ManifestValidationResult.ResultType.VALID,
            invalidityInfo=None
        )
    
    @staticmethod
    def invalid(invalidityType, invalidityInfo) -> Self:
        """
        NOTE: `invalidityType` and `invalidityInfo` must match those specified in `InvalidityInfo`.
        """
        
        return ManifestValidationResult(
            resultType=ManifestValidationResult.ResultType.INVALID,
            invalidityInfo=ManifestValidationResult.InvalidityInfo(
                invalidityType=invalidityType,
                info=invalidityInfo
            )
        )


# convenient classes
_ManifestInvalidityTypes = ManifestValidationResult.InvalidityInfo.InvalidityType

# override ManifestUtil methods for toy data
from src.mercury_nn.utils import dictElementToDict
def _getTags(manifest: ET._Element):
    tag_sets = [parseCondensedTags(child.text) for child in dictElementToDict(manifest)['tags']]
    tags = set()

    for tag_set in tag_sets:
        tags.update(tag_set)

    return tags

ManifestUtils.getTags = _getTags

# TODO: write tests
def validateManifest(manifest: ET._Element,
                     base_model_filter: Filter | None=None,
                     loadedTags: Dict[str, ET._Element] | None = None) \
                    -> ManifestValidationResult:

    if loadedTags is None:
        loadedTags = loadTags()
    
    if base_model_filter is None:
        base_model_filter = Filter.fromXMLElement(ET.parse(Config.baseModelFilterPath))

    # check syntax
    syntax_check_result = checkSyntax(manifest)

    if not syntax_check_result.isValid:
        return ManifestValidationResult.invalid(
            invalidityType=_ManifestInvalidityTypes.INVALID_SYNTAX,
            invalidityInfo=syntax_check_result.invalidityInfo
        )
    
    # check base model filter match
    base_model_match_result = matchFilter(base_model_filter, manifest)
    
    if not base_model_match_result.isSuccess:
        return ManifestValidationResult.invalid(
            invalidityType=_ManifestInvalidityTypes.FAILED_BASE_MODEL_FILTER_MATCH,
            invalidityInfo=base_model_match_result.failureInfo
        )
        
    tags = ManifestUtils.getTags(manifest)

    # check that there are no unknown tags
    if not tags.issubset(set(loadedTags.keys())):
        return ManifestValidationResult.invalid(
            invalidityType=_ManifestInvalidityTypes.UNKNOWN_TAGS,
            invalidityInfo=tags.difference(loadedTags)
        )
    
    # check that each tag matches
    for tag in tags:
        # try to match tag implicitly
        match_result = matchFilter(Filter.fromXMLElement(loadedTags[tag]), manifest, loadedTags)

        if not match_result.isSuccess:
            # TODO: indicate which tag mismatched
            return ManifestValidationResult.invalid(
                invalidityType=_ManifestInvalidityTypes.UNMATCHED_TAG,
                invalidityInfo=(tag, match_result.failureInfo)
            )
    
    return ManifestValidationResult.valid()
    