def dash_separated_to_upper_camel_case(name: str) -> str:
    """This function is used to convert identifiers
    (e.g., field names, type names, etc.)
    written as words separated by dash (-) into upper camel case.
    
    The identifier to convert is expected to be dash-separated words,
    with each word being alphanumeric;
    the first character should always be alphabetic.

    Args:
        name (str): The name to convert, dash-separated.

    Returns:
        str: The converted name, in upper camel case.
    """
    
    # validate
    exception_text = f'identifier "{name}" is invalid!'

    if len(name) == 0 or (not name[0].isalpha()):
        raise Exception(exception_text)

    words = name.split('-')
    for word in words:
        if len(word) == 0 or not word.isalnum():
            raise Exception(exception_text)

    # convert
    return ''.join(word[0].upper() + word[1:] for word in words)
    
    
def json2dataclass(name: str, desc: dict) -> str:
    """Generate dataclass definition from struct.

    :param name: str: The name of the dataclass to generate.
    :param desc (dict): The loaded json definition of the struct
    
    :returns: The generated dataclass definition.
    """
    
    # TODO
    return f"""@dataclass
class {name}:

"""
