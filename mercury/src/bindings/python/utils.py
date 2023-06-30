from typing import Tuple, Dict, List, Callable, Union, Any


class StructureInvalidException(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
    
    def __str__(self) -> str:
        return super().__str__()


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
    >>> template = {
    ...     'name': str,
    ...     'age': int,
    ...     'address': {
    ...         'street': str,
    ...         'city': str
    ...     },
    ...     'scores': [int, int, int]
    ... }
    >>> result = validate_pytree(pytree, template, isinstance)
    >>> print(result)
    True
    """

    if isinstance(template, (Tuple, List, Dict)):
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
        return predicate(pytree, template)

def tree_map(pytrees: List[Union[Dict, List, Tuple] | Any], mapper: Callable[..., Any]) -> Union[Dict, List, Tuple] | Any:
    """
    Map a function over multiple pytrees with identical structures.

    :param pytrees: A List of pytrees. Pytree can be a nested structure of Lists, Tuples, or Dictionaries.
    :type pytrees: List[Union[Dict, List, Tuple] | Any]
    :param mapper: The function to be mapped over the pytrees.
    :type mapper: Callable[..., Any]
    :return: A new pytree with the same structure as the input pytrees,
    where each element is the result of applying the function to the corresponding elements in the input pytrees.
    :rtype: Union[Dict, List, Tuple] | Any

    :raises ValueError: If the structures of the pytrees are not identical.

    Usage example:
    
    >>> def square(x, y, z):
    ...     return x ** 2 + y ** 2 + z ** 2
    >>> pytree_1 = [1, 2, 3]
    >>> pytree_2 = [4, 5, 6]
    >>> pytree_3 = [7, 8, 9]

    >>> result = tree_map([pytree_1, pytree_2, pytree_3], square)
    >>> print(result)
    [66, 93, 126]

    This function takes a List of pytrees and a function as input.
    It maps the function over the pytrees,
    applying the function to the corresponding leaf elements in the input pytrees.
    The resulting pytree has the same structure as the input pytrees,
    where each element is the result of applying the function to the corresponding leaf elements in the input pytrees.

    For example, if the input pytrees are ``pytree_1 = [1, 2, 3]``, ``pytree_2 = [4, 5, 6]``, and ``pytree_3 = [7, 8, 9]``,
    and the function is ``square(x) = x ** 2 + y ** 2 + z ** 2``, the result will be ``result = [66, 93, 126]`.
    """
    
    def is_internal_node(value: Any):
        return isinstance(value, (List, Tuple, Dict))

    if is_internal_node(pytrees[0]):
        if len(set(type(tree) for tree in pytrees)) > 1:
            raise StructureInvalidException('Structures of the pytrees are not identical!')
        
        if isinstance(pytrees[0], (List, Tuple)):
            if len(set(len(tree) for tree in pytrees)) > 1:
                raise StructureInvalidException('Pytrees have different lengths!')

            return type(pytrees[0])(tree_map(items, mapper) for items in zip(*pytrees))
        elif isinstance(pytrees[0], Dict):
            keys = [set(tree.keys()) for tree in pytrees]
            if not all(ks == keys[0] for ks in keys):
                raise StructureInvalidException('Pytrees have different keys!')
            
            return {key: tree_map([pytree[key] for pytree in pytrees], mapper) for key in pytrees[0].keys()}
        else:
            raise StructureInvalidException(f'Incorrect internal node type: {type(pytrees[0])}')
    else:
        if not all(not is_internal_node(tree) for tree in pytrees):
            raise StructureInvalidException('First pytree but not all pytrees are terminal!')
        
        return mapper(*pytrees)
