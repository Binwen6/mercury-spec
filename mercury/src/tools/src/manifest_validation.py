import xml.etree.ElementTree as ET

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'spec-language-interfaces'))

from python_interface.interface import (
    TagNames, AttributeNames, FilterOperationTypes, filterXMLfromArgs,
    TypeDeclarationTagNames, TypeDeclarationFilterOperationTypes, TypeDeclarationAttributeNames
)


# TODO: write tests
def checkSyntax(element: ET.Element) -> bool:
    match element.tag:
        case TagNames.dictType.value:
            # all children must be of named-field type
            children_tags = {child.tag for child in element}
            if children_tags != {TagNames.namedField.value}:
                # invalid tag for a child of dict
                return False
            
            children_validity = [checkSyntax(child) for child in element]
            
            if not all(children_validity):
                # at least one child is invalid
                return False
            
            # all children must have different names
            children_names = {child.attrib[AttributeNames.nameAttribute.value] for child in element}

            if len(children_names) != len(element):
                # duplicated names detected
                return False
            
            return True
        
        case TagNames.listType.value:
            return all(checkSyntax(child) for child in element)

        case TagNames.namedField.value:
            # element must have a "name" attribute
            if AttributeNames.nameAttribute.value not in element.attrib.keys():
                # element does not have a "name" attribute
                return False

            # length of children must be 1
            if len(element) != 1:
                # length of children is not 1
                return False
            
            return True

        case TagNames.string.value:
            if len(element) > 0:
                # child element is detected on a string element
                return False
            
            return True

        case TagNames.typeIdentifier.value:
            if len(element) != 1:
                # type identifier elements must have exactly one child
                return False

            return checkTypeDeclarationSyntax(element[0])

        case _:
            # invalid tag name
            return False


# TODO: write tests
def checkTypeDeclarationSyntax(element: ET.Element) -> bool:
    match element.tag:
        case TypeDeclarationTagNames.STRING.value | TypeDeclarationTagNames.BOOL.value:
            if len(element) > 0 or len(element.text) > 0:
                # a string / bool type declaration must have no children or enclosed content
                return False
            
            return True
        
        case TypeDeclarationTagNames.TENSOR.value:
            # all children must be of dim type
            children_tags = {child.tag for child in element}

            if children_tags != {TypeDeclarationTagNames.DIM.value}:
                # child tag is not dim
                return False
            
            return all(checkTypeDeclarationSyntax(child) for child in element)
        
        case TypeDeclarationTagNames.LIST.value:
            if len(element) != 1:
                # a list type declaration must have exactly one child
                return False
            
            return checkTypeDeclarationSyntax(element[0])
        
        case TypeDeclarationTagNames.TUPLE.value:
            return all(checkTypeDeclarationSyntax(child) for child in element)
        
        case TypeDeclarationTagNames.NAMED_VALUE_COLLECTION.value:
            # all children must be of named-value type
            children_tags = {child.tag for child in element}
            
            if children_tags != {TypeDeclarationTagNames.NAMED_VALUE.value}:
                # invalid tag for a child of dict
                return False
            
            children_validity = [checkTypeDeclarationSyntax(child) for child in element]
            
            if not all(children_validity):
                # at least one child is invalid
                return False
            
            # all children must have different names
            children_names = {child.attrib[TypeDeclarationAttributeNames.namedValueNameAttributeName.value] for child in element}

            if len(children_names) != len(element):
                # duplicated names detected
                return False
            
            return True
        
        case TypeDeclarationTagNames.NAMED_VALUE.value:
            # element must have a name attribute
            if TypeDeclarationAttributeNames.namedValueNameAttributeName.value not in element.attrib.keys():
                return False
            
            # element must have no children or enclosed content
            if len(element) > 0 or len(element.text) > 0:
                return False
            
            return True
        
        case TypeDeclarationTagNames.DIM.value:
            if len(element) > 0:
                # dim elements can have no children
                return False
            
            try:
                dim = int(element.text)
            except Exception:
                # dim element must be able to be parsed into an integer
                return False
            
            return True
        
        case _:
            # invalid tag name
            return False


# TODO: write tests
def checkFilterSyntax(element: ET.Element) -> bool:
    filterOpAttribName: str = AttributeNames.filterOperationTypeAttribute.value

    def hasFilterOpAttribute(element: ET.Element) -> bool:
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
            
                    return True
                
                case FilterOperationTypes.NONE.value:
                    if len(element) > 0 or len(element.text) > 0:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                
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
                    if len(element) > 0 or len(element.text) > 0:
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
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
                    
                    return False

                case FilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text != '':
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False

                case _:
                    # invalid filter operation type
                    return False

        case TagNames.typeIdentifier.value:
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
                    if len(element) > 0 or element.text != '':
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return True
                
                case _:
                    # invalid filter operation type
                    return False
        
        case _:
            # invalid tag
            return False


# TODO: write tests
def checkTypeDeclarationFilterSyntax(element: ET.Element) -> bool:
    filterOpAttribName: str = AttributeNames.filterOperationTypeAttribute.value

    def hasFilterOpAttribute(element: ET.Element) -> bool:
        return filterOpAttribName in element.keys()
    
    match element.tag:
        case TypeDeclarationTagNames.STRING.value | TypeDeclarationTagNames.BOOL.value:
            if len(element) > 0 or element.text != '':
                # primitive, atomic types declarations can have no children or enclosed content
                return False
            
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
                    if len(element) > 0 or element.text != '':
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return True
                
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
                    if len(element) > 0 or element.text != '':
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return True
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
                    if len(element) > 0 or element.text != '':
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return True
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
                    
                    return True
                
                case TypeDeclarationFilterOperationTypes.NONE.value:
                    if len(element) > 0 or element.text != '':
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return True
                
                case _:
                    # invalid filter operation type
                    return False
            
        case TypeDeclarationTagNames.NAMED_VALUE.value:
            if TypeDeclarationAttributeNames.namedValueNameAttributeName.value not in element.keys():
                # must have a name attribute
                return False
            
            if len(element) > 0 or element.text != '':
                # must have no children or enclosed content
                return False
            
            return True
            
        case TypeDeclarationTagNames.DIM.value:
            if not hasFilterOpAttribute(element):
                # must have a filter op attribute
                return False
            
            if len(element) > 0:
                # dim filters can have no children
                return False
            
            match element.attrib[filterOpAttribName]:
                case TypeDeclarationFilterOperationTypes.LESS_THAN.value | \
                        TypeDeclarationFilterOperationTypes.LESS_THAN_OR_EQUALS.value | \
                        TypeDeclarationFilterOperationTypes.GREATER_THAN.value | \
                        TypeDeclarationFilterOperationTypes.GREATER_THAN_OR_EQUALS.value:
                    
                    try:
                        dim = int(element.text)
                    except Exception:
                        # if the filter operation type is a comparison, enclosed text must be able to be parsed into an integer
                        return False
                    
                    return True
                case TypeDeclarationFilterOperationTypes.NONE.NONE:
                    if len(element) > 0 or element.text != '':
                        # if the filter operation is none, there cannot be children or enclosed content
                        return False
                    
                    return True
                case _:
                    # invalid filter operation type
                    return False
                
        case _:
            # invalid tag
            return False


def validateManifest(manifest: ET.Element):
    """Validates manifest data, throwing an error if the manifest is invalid.

    Args:
        manifest (ET.Element): The manifest data to validated, in parsed XML form.
    """
    
    # syntax check
    

def validateFilter(filterElement: ET.Element):
    """Validates a filter in XML form, throwing an error if the filter is invalid.

    Args:
        filterElement (ET.Element): The filter to validate.
    """
