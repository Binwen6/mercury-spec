def check_pairs(text: str):
    """
    Check whether the braces / brackets / square brackets in a string match.

    :param text: The input string to be checked.
    :type text: str
    :return: True if braces & brackets & square brackets match, False otherwise.
    :rtype: bool

    Examples:
    >>> check_braces("()")        # True
    True
    >>> check_braces("([])")      # True
    True
    >>> check_braces("({})")      # True
    True
    >>> check_braces("{{}")       # False
    False
    >>> check_braces("({)}")      # False
    False
    >>> check_braces("[{)]")      # False
    False
    """
    
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}

    for char in text:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if len(stack) == 0:
                return False
            if pairs[stack[-1]] != char:
                return False
            stack.pop()

    return len(stack) == 0
