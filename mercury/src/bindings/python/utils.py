from typing import Tuple, Dict, List, Callable, Union, Any


class StructureInvalidException(Exception):
    pass


def validate_pytree(pytree: Union[Dict, List, Tuple] | Any, template: Union[Dict, List, Tuple] | Any, predicate: Callable[[Any, Any], bool]) -> bool:
    """
    Validates whether a Python tree structure `pytree` conforms to a given template `template` using a provided predicate function `predicate`.

    :param pytree: The Python tree structure to be validated.
    :type pytree: Union[Dict, List, Tuple] | Any
    :param template: The template to validate against.
    :type template: Union[Dict, List, Tuple] | Any
    :param predicate: A function used to validate values. Should return `True` if the value is valid, `False` otherwise.
        The first argument is passed the value in the pytree; the second the value in the template.
    :type predicate: Callable[[Any, Any], bool]
    :return: Whether the `pytree` is valid according to the `template`.
    :rtype: bool

    The `validate_pytree` function traverses the `pytree` structure recursively,
    comparing the leaf node values in the `pytree` and `template` structures. 

    The function returns `True` if the `pytree` structure is valid according to the `template`,
    meaning that all leaf values in `pytree` are valid against their counterparts in `template`.
    If there is a mismatch, either due to a missing key, incorrect type, or failing predicate, the function returns `False`.

    Example Usage:
    
    >>> pytree = {
    ...     'name': 'Alice',
    ...     'age': 25,
    ...     'address': {
    ...         'street': '1234 Elm St',
    ...         'city': 'Sample City'
    ...     },
    ...     'scores': [90, 85, 95]
    ... }
    >>>
    >>> template = {
    ...     'name': str,
    ...     'age': int,
    ...     'address': {
    ...         'street': str,
    ...         'city': str
    ...     },
    ...     'scores': [int, int, int]
    ... }
    >>>
    >>> result = validate_pytree(pytree, template, isinstance)
    >>> print(result)
    True
    """

    if isinstance(template, Tuple) or isinstance(template, List) or isinstance(template, Dict):
        # composed type
        if (isinstance(template, Tuple) and isinstance(pytree, Tuple)) or \
            (isinstance(template, List) and isinstance(pytree, List)):
            # sequence type
            if len(pytree) != len(template) or \
                (not all(
                    validate_pytree(py_subtree, template_subtree, predicate)
                    for py_subtree, template_subtree in zip(pytree, template))):
                return False
            else:
                return True
        elif isinstance(template, Dict) and isinstance(pytree, Dict):
            # Dict
            for key in template.keys():
                if (not key in pytree.keys()) or \
                    (not validate_pytree(pytree[key], template[key], predicate)):
                    return False
            return True
        else:
            return False
    else:
        # terminal node
        if isinstance(pytree, Tuple) or isinstance(pytree, List) or isinstance(pytree, Dict):
            return False
        else:
            return predicate(pytree, template)