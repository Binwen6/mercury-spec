import xml.etree.ElementTree as ET

from .spec_interface import TagNames, AttributeNames, FilterOperationTypes
from .exceptions import InvalidTagException, InvalidFilterOperationTypeException

class FilterMatchResult:
    SUCCESS = 0
    FAILURE = 1
    

def match_filter(filter: ET.Element, element: ET.Element) -> FilterMatchResult:
    """
    Match model metadata against a filter.
    Typically, both `filter` and `element` are obtained by parsing an xml document.

    Args:
        filter (ET.Element): The filter to match against.
        element (ET.Element): The element to match.
    """
    
    if element.tag != filter.tag:
        return FilterMatchResult.FAILURE
    
    match filter.tag:
        case TagNames.dictType.value:
            match filter.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                case FilterOperationTypes.all.value:
                    # match each child element
                    # get all key-value pairs from named-field elements & filters
                    element_children_dict = {sub_element.attrib[AttributeNames.nameAttribute.value]: sub_element[0] for sub_element in element}
                    filter_children_dict = {sub_filter.attrib[AttributeNames.nameAttribute.value]: sub_filter[0] for sub_filter in filter}

                    if not set(filter_children_dict.keys()).issubset(set(element_children_dict.keys())):
                        return FilterMatchResult.FAILURE

                    return FilterMatchResult.SUCCESS \
                        if all(match_filter(filter_children_dict[key], element_children_dict[key]) == FilterMatchResult.SUCCESS
                               for key in filter_children_dict.keys()) \
                        else FilterMatchResult.FAILURE
                case FilterOperationTypes.none.value:
                    # since tag is compared in the beginning, we can just return success.
                    return FilterMatchResult.SUCCESS
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.listType.value:
            match filter.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                case FilterOperationTypes.all.value:
                    if len(element) < len(filter):
                        return FilterMatchResult.FAILURE
                    
                    # assume the list is ordered, match each sub-filter v.s. sub-element in order
                    return FilterMatchResult.SUCCESS \
                        if all(match_filter(sub_filter, sub_element) == FilterMatchResult.SUCCESS
                               for sub_filter, sub_element in zip(filter, element)) \
                        else FilterMatchResult.FAILURE
                case FilterOperationTypes.none.value:
                    return FilterMatchResult.SUCCESS
        case TagNames.namedField.value:
            # just raise since it should be guaranteed that named field will always be unwrapped before calling `match`
            raise InvalidTagException()
        case TagNames.string.value:
            match filter.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                # TODO: add more filter types for strings, e.g., regular expressions
                case FilterOperationTypes.none.value:
                    return FilterMatchResult.SUCCESS
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.typeIdentifier.value:
            match filter.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                # TODO: add more filter types for type identifiers
                case FilterOperationTypes.none.value:
                    return FilterMatchResult.SUCCESS
                case _:
                    raise InvalidFilterOperationTypeException()
        case TagNames.time.value:
            match filter.attrib[AttributeNames.filterOperationTypeAttribute.value]:
                # TODO: add more filter types for time
                case FilterOperationTypes.none.value:
                    return FilterMatchResult.SUCCESS
                case _:
                    raise InvalidFilterOperationTypeException()
        case _:
            raise InvalidTagException()