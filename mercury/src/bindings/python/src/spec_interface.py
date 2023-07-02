from enum import Enum


class TagNames(Enum):
    dictType = 'dict'
    listType = 'list'
    namedField = 'named-field'
    string = 'string'
    typeIdentifier = 'type-identifier'
    time = 'time'


class AttributeNames(Enum):
    filterOperationTypeAttribute = 'filter'
    nameAttribute = 'name'


class FilterOperationTypes(Enum):
    none = 'none'
    all = 'all'